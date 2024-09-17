from django.contrib.auth.models import User
from django.db import models


class OneArticle(models.Model):
    """Модель для получения одной статьи"""

    author_profile = models.URLField(help_text='Ссылка на профиль автора')
    author = models.CharField(help_text='Имя автора')
    author_rating = models.CharField(help_text="Рейтинг автора")
    title = models.CharField(help_text="Название статьи")
    content = models.CharField(help_text="Содержание стать")
    date = models.CharField(help_text="Дата публикации")
    rating = models.CharField(help_text="Рейтинг статьи")
    bookmarks = models.CharField(help_text="Количество добавления в закладки")
    comments = models.CharField(help_text="Комментарии")

    def __str__(self):
        return f"{self.title}: {self.author}"



class SearchArticles(models.Model):
    """Модель для хранения поисковых запросов"""

    SEARCHING_CHOICES = [
        ('relevance', 'relevance'),
        ('date', 'date'),
        ('rating', 'rating')

    ]
    PARSING_CHOICES = [
        ('list', 'list_of_articles'),
        ('first', 'first_article'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    searching_key = models.CharField(help_text='Поисковый запрос')
    searching_filter = models.CharField(choices=SEARCHING_CHOICES, default='relevance',help_text='Способ фильтрации')
    parsing_options = models.CharField(choices=PARSING_CHOICES, default='first',help_text='Как парсить')

    def __str__(self):
        return f'{self.user} {self.searching_key}'
