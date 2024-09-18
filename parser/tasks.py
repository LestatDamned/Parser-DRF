from celery import shared_task

from .parser_script import parsing_one_article, parsing_list_articles
from .models import Article, User, HistorySearch


@shared_task(name="parsing_one_article")
def start_parser(searching_key, user_id, search_id):
    result = parsing_one_article(searching_key)

    result = Article.objects.create(
    user = User.objects.get(pk=user_id),
    search_id = HistorySearch.objects.get(pk=search_id),
    article_link = result['article_link'],
    title = result['title'],
    author_profile = result['author_profile'],
    author = result['author'],
    author_rating = result['author_rating'],
    content = result['content'],
    date = result['date'],
    rating = result['rating'],
    bookmarks = result['bookmarks'],
    comments = result['comments'],
    )
    return search_id

@shared_task(name="parsing_list_articles")
def start_list_parser(searching_key, user_id, search_id):
    result = parsing_list_articles(searching_key)

    for article in result:
        Article.objects.create(
            user = User.objects.get(pk=user_id),
            search_id=HistorySearch.objects.get(pk=search_id),
            article_link = article['article_link'],
            title = article['title'],
            author_profile = article['author_profile'],
            author = article['author'],
            author_rating = article['author_rating'],
            content = article['content'],
            date = article['date'],
            rating = article['rating'],
            bookmarks = article['bookmarks'],
            comments = article['comments'],
        )
    return search_id