# -*- coding: utf-8 -*-
__author__ = 'gzp'

from django.db import migrations


def fix_book_data(apps, schema_editor):
    Book = apps.get_model('make_good_use_of_migrations', 'Book')
    Author = apps.get_model('make_good_use_of_migrations', 'Author')
    for book in Book.objects.all():
        author, _ = Author.objects.get_or_create(name='%s author' % book.name)
        book.author = author
        book.save()


class Migration(migrations.Migration):
    dependencies = [
        ('make_good_use_of_migrations', '0003_auto_20181204_0533'),
    ]

    operations = [
        migrations.RunPython(fix_book_data)
    ]
