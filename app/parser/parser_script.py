from abc import ABC, abstractmethod

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer


def send_progress(user_id=None, percent=None, task_id=None, task_state=None, result_id=None, type_message=None):
    """
    Функция для отправления сообщений по Websocket.

    :param user_id: ID пользователя котору отправляется сообщение.
    :param percent: Процент выполнения задачи (для percent_message).
    :param task_id: ID задачи которой мы отслеживаем (для parsing_status).
    :param task_state: Состояние задачи которую отслеживаем (для parsing_status).
    :param result_id: ID результата парсинга (для parsing_status).
    :param type_message: Тип сообщения который мы хоти отправить.
    """

    channel_layer = get_channel_layer()
    message_dict = {
        'percent_message': {
            "type": "percent_message",
            "message": f"{percent}%" if percent is not None else "0%",
        },
        "parsing_status": {
            "type": "parsing_status",
            "status": task_state,
            "task_id": task_id,
            "result_id": result_id if result_id is not None else "to be determined",
        }
    }
    async_to_sync(channel_layer.group_send)(f'user_{user_id}', message_dict.get(type_message))


class ArticleParser(ABC):
    """
    Абстрактный класс для шаблона классов парсера.

    Attributes:
        url: Адрес для поиска статьи.
        article_info: Список принимающий ссылки на конкретные статьи, если статей нет,
        выводит сообщение об отсутствие статей.
        soup: Экземпляр класса BeautifulSoup для парсинга статьи.
        soup_comments: Экземпляр класса BeautifulSoup для парсинга комментариев.
        searching_keyword: Поисковый запрос.
        searching_filter: Фильтр поиска.
        search_result: Словарь с распарсенной статьей.
        no_articles: False по умолчанию, если статей нет то True.
        result: Список с результатами парсинга.
        user_id: ID пользователя, который запросил парсинг.
    """

    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        }
        self.url = None
        self.article_info = None
        self.soup = None
        self.soup_comments = None
        self.searching_keyword = None
        self.searching_filter = "relevance"
        self.search_result = None
        self.no_articles = False
        self.result = []
        self.user_id = None

    def start_parsing(self):
        """Шаблон выполнения функций"""

        self.get_url_searching()
        self.check_and_get_available_article()
        self.get_article_url()
        self.parsing_template()
        return self.result

    @abstractmethod
    def check_and_get_available_article(self):
        """Проверяет если ли статьи по поисковому запросу"""
        pass

    @abstractmethod
    def get_article_url(self):
        """Находит ссылки на статьи"""
        pass

    def get_url_searching(self):
        """Получает поисковый запрос и делает ссылку на поиск статьи"""

        url = f"https://habr.com/ru/search/?q={self.searching_keyword}&target_type=posts&order={self.searching_filter}"
        req = requests.get(url, headers=self.headers)
        src = req.text
        self.search_result = BeautifulSoup(src, "lxml")
        send_progress(self.user_id, percent=10, type_message="percent_message")

    def parsing_template(self):
        """Выполняет пасинг найденный статей"""

        send_progress(user_id=self.user_id, percent=50, type_message="percent_message")

        if self.no_articles:  # если нет статей, то выводится сообщение об отсутствии статей
            return print(self.article_info)

        else:
            for progress, article in enumerate(self.article_info, start=1):
                req = requests.get(article["article_link"], headers=self.headers)
                src = req.text
                req_comments = requests.get(article["article_comments"], headers=self.headers)
                src_comments = req_comments.text
                soup = BeautifulSoup(src, "lxml")
                soup_comments = BeautifulSoup(src_comments, "lxml")

                article_title = soup.find(class_="tm-title tm-title_h1").text
                article_body = soup.find("div", id="post-content-body").text
                article_author = soup.find(class_="tm-user-info__username").text
                author_profile_link = soup.find(class_="tm-user-info__username")["href"]
                article_author_profile = f"https://habr.com{author_profile_link}"
                article_date_raw = soup.find(class_="tm-article-datetime-published")
                article_date = article_date_raw.find("time")["title"]
                try:
                    article_rating = soup.find("span", class_="tm-votes-meter__value").text
                except AttributeError:
                    article_rating = None
                article_author_rating = soup.find(class_="tm-votes-lever__score-counter "
                                                         "tm-votes-lever__score-counter_rating "
                                                         "tm-votes-lever__score-counter").text
                article_bookmark = soup.find(class_="bookmarks-button__counter").text

                all_comments = soup_comments.find_all(class_="tm-comment-thread")
                rating_find_alias = ("tm-votes-meter__value tm-votes-meter__value_positive "
                                     "tm-votes-meter__value_appearance-comment "
                                     "tm-votes-meter__value_rating tm-votes-meter__value")
                filtered_comments = [comment for comment in all_comments
                                     if comment.find(class_=rating_find_alias) is not None]
                sorted_list_comments = sorted(filtered_comments,
                                              key=lambda x: int(x.find(class_=rating_find_alias).text), reverse=True)
                if len(sorted_list_comments) > 5:
                    sorted_list_comments = sorted_list_comments[:5]

                comment_list = []

                for number, comment in enumerate(sorted_list_comments, start=1):
                    comment_list.append((f"Рейтинг: {comment.find(class_=rating_find_alias).text}",
                                         f"Комментарий: {comment.find(class_="tm-comment__body-content").text}"))

                result_dict = {
                    "article_link": article["article_link"],
                    "title": article_title,
                    "author_profile": article_author_profile,
                    "author": article_author,
                    "author_rating": article_author_rating,
                    "content": article_body,
                    "date": article_date,
                    "rating": article_rating,
                    "bookmarks": article_bookmark,
                    "comments": comment_list,
                }

                send_progress(user_id=self.user_id, percent=((progress * 5) + 50), type_message="percent_message")

                self.result.append(result_dict)


class ParsingOneArticle(ArticleParser):
    """Класс парсера для парсинга первой статьи по поисковому запросу"""

    def __init__(self, searching_keyword=None, searching_filter="relevance", user_id=None):
        super().__init__()
        self.searching_keyword = searching_keyword
        self.searching_filter = searching_filter
        self.search_result = None
        self.user_id = user_id

    def check_and_get_available_article(self):
        no_articles = self.search_result.find("div", class_="tm-empty-placeholder__text")
        if no_articles:
            self.no_articles = True
        self.search_result = self.search_result.find("a", class_="tm-title__link")["href"]
        send_progress(self.user_id, percent=20, type_message="percent_message")

    def get_article_url(self):
        send_progress(self.user_id, percent=30, type_message="percent_message")
        self.article_info = []
        if self.no_articles:
            self.article_info = [{"message": "По вашему запросу статьи не найдены"}]
        else:
            self.article_info.append(
                {"article_link": f"https://habr.com{self.search_result}",
                 "article_comments": f"https://habr.com{self.search_result}comments/"}
            )


class ParsingListArticles(ArticleParser):
    """Класс парсера для поиска первых десяти статей по поисковому запросу"""

    def __init__(self, searching_keyword=None, searching_filter="relevance", user_id=None):
        super().__init__()
        self.searching_keyword = searching_keyword
        self.searching_filter = searching_filter
        self.user_id = user_id

    def check_and_get_available_article(self):
        no_articles = self.search_result.find("div", class_="tm-empty-placeholder__text")
        if no_articles:
            self.no_articles = True
        self.search_result = self.search_result.find_all("article", class_="tm-articles-list__item")
        send_progress(user_id=self.user_id, percent=20, type_message="percent_message")

    def get_article_url(self):
        send_progress(user_id=self.user_id, percent=30, type_message="percent_message")

        if self.no_articles:
            self.article_info = [{"message": "По вашему запросу статьи не найдены"}]
        else:
            self.article_info = []
            for article in self.search_result[:10]:
                article = article.find("a", class_="tm-title__link")["href"]
                article_link = f"https://habr.com{article}"
                article_comments = f"https://habr.com{article}comments/"

                self.article_info.append(
                    {"article_link": article_link,
                     "article_comments": article_comments}
                )
