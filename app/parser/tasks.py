from asgiref.sync import async_to_sync
from celery import shared_task
from celery.result import AsyncResult
from channels.layers import get_channel_layer

from .parser_script import parsing_one_article, parsing_list_articles, ParsingListArticles
from .models import Article, User, HistorySearch


@shared_task(name="parsing_one_article")
def start_parser(searching_key, user_id, search_id):
    result = parsing_one_article(searching_key)

    parsing_result_unpacking(result, user_id, search_id)

    return search_id


@shared_task(bind=True, name="parsing_list_articles")
def start_list_parser(self, searching_key, user_id, search_id):
    channel_layer = get_channel_layer()
    self.update_state(state="PARSING")
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'parsing_status',
            'status': "PARSING",
            'task_id': self.request.id,
            'result_id': search_id,
        }
    )
    parsing = ParsingListArticles(searching_keyword = searching_key)
    result = parsing.start_parsing()
    total_articles = len(result)


    for number, article in enumerate(result, start=1):
        parsing_result_unpacking(article, user_id, search_id)
        # self.update_state(state="PROGRESS", meta={"number": number, "total": total_articles})
        # async_to_sync(channel_layer.group_send)(
        #     f'user_{user_id}',
        #     {
        #         'type': 'parsing_status',
        #         'status': "PROGRESS",
        #         'task_id': self.request.id,
        #         'result_id': search_id,
        #     }
        # )
        return search_id


def parsing_result_unpacking(result, user_id, search_id):
    return Article.objects.create(
        user=User.objects.get(pk=user_id),
        search_id=HistorySearch.objects.get(pk=search_id),
        article_link=result["article_link"],
        title=result["title"],
        author_profile=result["author_profile"],
        author=result["author"],
        author_rating=result["author_rating"],
        content=result["content"],
        date=result["date"],
        rating=result["rating"],
        bookmarks=result["bookmarks"],
        comments=result["comments"],
    )


