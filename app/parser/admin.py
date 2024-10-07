from django.contrib import admin

from .models import Article, HistorySearch

admin.site.register(Article)
admin.site.register(HistorySearch)
