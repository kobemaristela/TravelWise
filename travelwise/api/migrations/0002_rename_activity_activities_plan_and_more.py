# Generated by Django 4.2.3 on 2023-07-25 00:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activities',
            old_name='activity',
            new_name='plan',
        ),
        migrations.RenameField(
            model_name='chat',
            old_name='activity',
            new_name='plan',
        ),
    ]
