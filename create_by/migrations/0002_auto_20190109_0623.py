# Generated by Django 2.1.4 on 2019-01-09 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create_by', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='book',
            name='name',
            field=models.CharField(max_length=32),
        ),
    ]