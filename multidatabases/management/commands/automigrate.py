# -*- coding: utf-8 -*-
__author__ = 'gzp'

from importlib import import_module

from django.apps import apps
from django.core.management.base import CommandError
from django.core.management.sql import (
    emit_post_migrate_signal, emit_pre_migrate_signal,
)
from django.db import connections
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import AmbiguityError
from django.db.migrations.state import ModelState, ProjectState
from django.utils.module_loading import module_has_submodule, import_string

from django.core.management.commands.migrate import Command as BaseMigrateCommand
from django import conf


class Command(BaseMigrateCommand):
    """
    用于多数据库migrate 不需要指定--database
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'migration_name', nargs='?',
            help='Database state will be brought to the state after that '
                 'migration. Use the name "zero" to unapply all migrations.',
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--fake', action='store_true', dest='fake',
            help='Mark migrations as run without actually running them.',
        )
        parser.add_argument(
            '--fake-initial', action='store_true', dest='fake_initial',
            help='Detect if tables already exist and fake-apply initial migrations if so. Make sure '
                 'that the current database schema matches your initial migration before using this '
                 'flag. Django will only check for an existing table name.',
        )
        parser.add_argument(
            '--run-syncdb', action='store_true', dest='run_syncdb',
            help='Creates tables for apps without migrations.',
        )

    def _filter_targets(self, connection, targets, db_routers):
        filtered_targets = []
        for app_label, target in targets:
            exclude_target = False
            for router in db_routers:
                if router.allow_migrate(connection.alias, app_label) is False:
                    exclude_target = True
                    break

            if not exclude_target:
                filtered_targets.append((app_label, target))

        return filtered_targets

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.interactive = options['interactive']

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_config in apps.get_app_configs():
            if module_has_submodule(app_config.module, "management"):
                import_module('.management', app_config.name)

        db_routers = [import_string(router)() for router in conf.settings.DATABASE_ROUTERS]
        for connection in connections.all():
            # Hook for backends needing any database preparation
            connection.prepare_database()
            # Work out which apps have migrations and which do not
            executor = MigrationExecutor(connection, self.migration_progress_callback)

            # Raise an error if any migrations are applied before their dependencies.
            executor.loader.check_consistent_history(connection)

            # Before anything else, see if there's conflicting apps and drop out
            # hard if there are any
            conflicts = executor.loader.detect_conflicts()
            if conflicts:
                name_str = "; ".join(
                    "%s in %s" % (", ".join(names), app)
                    for app, names in conflicts.items()
                )
                raise CommandError(
                    "Conflicting migrations detected; multiple leaf nodes in the "
                    "migration graph: (%s).\nTo fix them run "
                    "'python manage.py makemigrations --merge'" % name_str
                )

            # If they supplied command line arguments, work out what they mean.
            targets, target_app_labels_only = self._get_targets(connection, executor, db_routers, options)

            plan = executor.migration_plan(targets)
            run_syncdb = options['run_syncdb'] and executor.loader.unmigrated_apps

            # Print some useful info
            if self.verbosity >= 1:
                self.stdout.write(self.style.MIGRATE_HEADING("Operations to perform:"))
                if run_syncdb:
                    self.stdout.write(
                        self.style.MIGRATE_LABEL(
                            "  Synchronize unmigrated apps: "
                        ) + (", ".join(sorted(executor.loader.unmigrated_apps)))
                    )
                if target_app_labels_only:
                    self.stdout.write(
                        self.style.MIGRATE_LABEL(
                            "  Apply all migrations: "
                        ) + (", ".join(sorted({a for a, n in targets})) or "(none)")
                    )
                else:
                    if targets[0][1] is None:
                        self.stdout.write(self.style.MIGRATE_LABEL(
                            "  Unapply all migrations: ") + "%s" % (targets[0][0],)
                        )
                    else:
                        self.stdout.write(self.style.MIGRATE_LABEL(
                            "  Target specific migration: ") + "%s, from %s"
                            % (targets[0][1], targets[0][0])
                        )

            pre_migrate_state = executor._create_project_state(with_applied_migrations=True)
            pre_migrate_apps = pre_migrate_state.apps
            emit_pre_migrate_signal(
                self.verbosity, self.interactive, connection.alias, apps=pre_migrate_apps, plan=plan,
            )

            # Run the syncdb phase.
            if run_syncdb:
                self._syncdb_phase(connection, executor)

            # Migrate!
            self._migrate(plan, connection, executor, pre_migrate_state, targets, options)

    def _get_targets(self, connection, executor, db_routers, options):
        target_app_labels_only = True
        if options['migration_name']:
            app_label, migration_name = options['app_label'], options['migration_name']
            if app_label not in executor.loader.migrated_apps:
                raise CommandError(
                    "App '%s' does not have migrations." % app_label
                )
            if migration_name == "zero":
                targets = [(app_label, None)]
            else:
                try:
                    migration = executor.loader.get_migration_by_prefix(app_label, migration_name)
                except AmbiguityError:
                    raise CommandError(
                        "More than one migration matches '%s' in app '%s'. "
                        "Please be more specific." %
                        (migration_name, app_label)
                    )
                except KeyError:
                    raise CommandError("Cannot find a migration matching '%s' from app '%s'." % (
                        migration_name, app_label))
                targets = [(app_label, migration.name)]
            target_app_labels_only = False
        else:
            targets = executor.loader.graph.leaf_nodes()

        targets = self._filter_targets(connection, targets, db_routers)
        return targets, target_app_labels_only

    def _syncdb_phase(self, connection, executor):
        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_HEADING("Synchronizing apps without migrations:"))
        self.sync_apps(connection, executor.loader.unmigrated_apps)

    def _migrate(self, plan, connection, executor, pre_migrate_state, targets, options):
        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_HEADING("Running migrations:"))
        if not plan:
            if self.verbosity >= 1:
                self.stdout.write("  No migrations to apply.")
                # If there's changes that aren't in migrations yet, tell them how to fix it.
                autodetector = MigrationAutodetector(
                    executor.loader.project_state(),
                    ProjectState.from_apps(apps),
                )
                changes = autodetector.changes(graph=executor.loader.graph)
                if changes:
                    self.stdout.write(self.style.NOTICE(
                        "  Your models have changes that are not yet reflected "
                        "in a migration, and so won't be applied."
                    ))
                    self.stdout.write(self.style.NOTICE(
                        "  Run 'manage.py makemigrations' to make new "
                        "migrations, and then re-run 'manage.py migrate' to "
                        "apply them."
                    ))
            fake = False
            fake_initial = False
        else:
            fake = options['fake']
            fake_initial = options['fake_initial']
        post_migrate_state = executor.migrate(
            targets, plan=plan, state=pre_migrate_state.clone(), fake=fake,
            fake_initial=fake_initial,
        )
        # post_migrate signals have access to all models. Ensure that all models
        # are reloaded in case any are delayed.
        post_migrate_state.clear_delayed_apps_cache()
        post_migrate_apps = post_migrate_state.apps

        # Re-render models of real apps to include relationships now that
        # we've got a final state. This wouldn't be necessary if real apps
        # models were rendered with relationships in the first place.
        with post_migrate_apps.bulk_update():
            model_keys = []
            for model_state in post_migrate_apps.real_models:
                model_key = model_state.app_label, model_state.name_lower
                model_keys.append(model_key)
                post_migrate_apps.unregister_model(*model_key)
        post_migrate_apps.render_multiple([
            ModelState.from_model(apps.get_model(*model)) for model in model_keys
        ])

        # Send the post_migrate signal, so individual apps can do whatever they need
        # to do at this point.
        emit_post_migrate_signal(
            self.verbosity, self.interactive, connection.alias, apps=post_migrate_apps, plan=plan,
        )
