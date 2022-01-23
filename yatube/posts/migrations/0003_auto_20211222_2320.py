# Generated by Django 2.2.9 on 2021-12-22 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20211221_0332'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='slug',
            new_name='slug_g',
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_posts', to='posts.Group'),
        ),
    ]
