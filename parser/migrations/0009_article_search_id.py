# Generated by Django 5.1.1 on 2024-09-18 15:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0008_article_rename_searcharticles_historysearch_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='search_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='parser.historysearch'),
        ),
    ]