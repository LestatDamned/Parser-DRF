from celery import shared_task

from .models import Article, User, HistorySearch
from .parser_script import ParsingListArticles, ParsingOneArticle, send_progress


@shared_task(bind=True, name="parsing_one_article")
def start_parser(self, searching_key, user_id, search_id):
    """Celery задача для парсинга первой статьи"""

    parsing = ParsingOneArticle(searching_keyword=searching_key, user_id=user_id)
    result = parsing.start_parsing()

    for progress in range(2, 11):
        send_progress(user_id=user_id, percent=((progress * 5) + 50), type_message="percent_message")

    parsing_result_unpacking(result[0], user_id, search_id)

    send_progress(user_id=user_id, task_id=self.request.id, result_id=search_id,
                  type_message="parsing_status", task_state="FINISHED")

    return search_id


@shared_task(bind=True, name="parsing_list_articles")
def start_list_parser(self, searching_key, user_id, search_id):
    """Celery задача для парсинга списка статей"""

    parsing = ParsingListArticles(searching_keyword=searching_key, user_id=user_id)
    result = parsing.start_parsing()

    for article in result:
        parsing_result_unpacking(article, user_id, search_id)
    send_progress(user_id=user_id, task_id=self.request.id, result_id=search_id,
                  type_message="parsing_status", task_state="FINISHED")
    return search_id


def parsing_result_unpacking(article, user_id, search_id):
    """Функция распаковки статей из списка"""

    tmp = Article.objects.create(
        user=User.objects.get(pk=user_id),
        search_id=HistorySearch.objects.get(pk=search_id),
        article_link=article["article_link"],
        title=article["title"],
        author_profile=article["author_profile"],
        author=article["author"],
        author_rating=article["author_rating"],
        content=article["content"],
        date=article["date"],
        rating=article["rating"],
        bookmarks=article["bookmarks"],
        comments=article["comments"],
    )
    tmp.save()
