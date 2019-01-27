# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.test.testcases import TransactionTestCase


class TestCase(TransactionTestCase):
    """
    此类修复 Django TestCase 中由于使用了多数据库，但是 multi_db 并未指定多数据库，单元测试依然只是在一个数据库上运行。
    但是源码中的 connections_support_transactions 将所有数据库都包含进来了，导致在同时使用 MangoDB 和 MySQL 数据库时，
    MySQL 数据库无法回滚，清空了所有的初始化数据，导致单元测试无法使用初始化的数据。
    """

    @classmethod
    def _databases_support_transactions(cls):
        return all(
            conn.features.supports_transactions
            for conn in connections.all()
            if conn.alias in cls._databases_names()
        )

    @classmethod
    def _databases_names(cls, include_mirrors=True):
        # If the test case has a multi_db=True flag, act on all databases,
        # including mirrors or not. Otherwise, just on the default DB.
        if cls.multi_db:
            return [
                alias for alias in connections
                if include_mirrors or not connections[alias].settings_dict['TEST']['MIRROR']
            ]
        else:
            return [DEFAULT_DB_ALIAS]

    @classmethod
    def _enter_atomics(cls):
        """Open atomic blocks for multiple databases."""
        atomics = {}
        for db_name in cls._databases_names():
            atomics[db_name] = transaction.atomic(using=db_name)
            atomics[db_name].__enter__()
        return atomics

    @classmethod
    def _rollback_atomics(cls, atomics):
        """Rollback atomic blocks opened by the previous method."""
        for db_name in reversed(cls._databases_names()):
            transaction.set_rollback(True, using=db_name)
            atomics[db_name].__exit__(None, None, None)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls._databases_support_transactions():
            return
        cls.cls_atomics = cls._enter_atomics()

        if cls.fixtures:
            for db_name in cls._databases_names(include_mirrors=False):
                try:
                    call_command('loaddata', *cls.fixtures, **{'verbosity': 0, 'database': db_name})
                except Exception:
                    cls._rollback_atomics(cls.cls_atomics)
                    raise
        try:
            cls.setUpTestData()
        except Exception:
            cls._rollback_atomics(cls.cls_atomics)
            raise

    @classmethod
    def tearDownClass(cls):
        if cls._databases_support_transactions():
            cls._rollback_atomics(cls.cls_atomics)
            for conn in connections.all():
                conn.close()
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        """Load initial data for the TestCase."""
        pass

    def _should_reload_connections(self):
        if self._databases_support_transactions():
            return False
        return super()._should_reload_connections()

    def _fixture_setup(self):
        if not self._databases_support_transactions():
            # If the backend does not support transactions, we should reload
            # class data before each test
            self.setUpTestData()
            return super()._fixture_setup()

        assert not self.reset_sequences, 'reset_sequences cannot be used on TestCase instances'
        self.atomics = self._enter_atomics()

    def _fixture_teardown(self):
        if not self._databases_support_transactions():
            return super()._fixture_teardown()
        try:
            for db_name in reversed(self._databases_names()):
                if self._should_check_constraints(connections[db_name]):
                    connections[db_name].check_constraints()
        finally:
            self._rollback_atomics(self.atomics)

    def _should_check_constraints(self, connection):
        return (
                connection.features.can_defer_constraint_checks and
                not connection.needs_rollback and connection.is_usable()
        )
