# Generated by Django 5.1.6 on 2025-06-30 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lms_core', '0010_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
