from django.db import migrations

"""
make_good_use_of_migrations 是App的名字
"""


def init_book_data(apps, schema_editor):
    Book = apps.get_model('make_good_use_of_migrations', 'Book')
    init_data = ['Hamlet', 'Tempest', 'The Little Prince']
    for name in init_data:
        book = Book(name=name)
        book.save()


class Migration(migrations.Migration):
    dependencies = [
        ('make_good_use_of_migrations', '0001_initial'),
    ]

    # 这里要注意dependencies为上一次migrations的文件名称

    operations = [
        migrations.RunPython(init_book_data)
    ]
