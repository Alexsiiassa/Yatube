# Generated by Django 2.2.9 on 2021-12-22 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20211222_2320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='slug_g',
            new_name='slug',
        ),
    ]
