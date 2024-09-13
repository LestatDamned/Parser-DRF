# Generated by Django 5.1.1 on 2024-09-11 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0003_delete_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListArticles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Название статьи')),
                ('link', models.URLField(help_text='URL ссылка на статью')),
                ('author', models.CharField(help_text='Имя автора')),
                ('author_link', models.URLField(help_text='URL ссылка на автора')),
                ('date', models.CharField(help_text='Дата публикации')),
                ('content', models.CharField(help_text='Содержание')),
                ('rating', models.CharField(help_text='Рейтинг статьи')),
                ('bookmarks', models.CharField(help_text='Количество добавлений в закладки')),
                ('comments', models.CharField(help_text='Количество комментариев')),
            ],
        ),
    ]
