# Generated by Django 5.1.1 on 2024-09-10 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0002_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
