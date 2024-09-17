from celery import shared_task
from .parser_script import parsing_one_article, parsing_list_articles_new

@shared_task
def start_parser(searching_key):
    return parsing_one_article(searching_key)

@shared_task
def start_list_parser(searching_key):
    return parsing_list_articles_new(searching_key)