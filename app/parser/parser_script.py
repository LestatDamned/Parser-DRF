import requests
from pprint import pprint
from bs4 import BeautifulSoup


def parsing(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }

    article_link = f"https://habr.com{url}"
    article_comments = f"https://habr.com{url}comments/"
    req = requests.get(article_link, headers=headers)
    src = req.text
    req_comments = requests.get(article_comments, headers=headers)
    src_comments = req_comments.text

    soup = BeautifulSoup(src, "lxml")
    soup_comments = BeautifulSoup(src_comments, "lxml")

    article_title = soup.find(class_="tm-title tm-title_h1").text
    article_body = soup.find("div", id="post-content-body").get_text(strip=True)
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
                                             "tm-votes-lever__score-counter_rating tm-votes-lever__score-counter").text
    article_bookmark = soup.find(class_="bookmarks-button__counter").text
    all_comments = soup_comments.find_all(class_="tm-comment-thread")
    rating_find_alias = ("tm-votes-meter__value tm-votes-meter__value_positive "
                         "tm-votes-meter__value_appearance-comment tm-votes-meter__value_rating tm-votes-meter__value")
    filtered_comments = [comment for comment in all_comments if comment.find(class_=rating_find_alias) is not None]
    sorted_list_comments = sorted(filtered_comments, key=lambda x: int(x.find(class_=rating_find_alias).text)
                                  , reverse=True)
    if len(sorted_list_comments) > 5:
        sorted_list_comments = sorted_list_comments[:5]

    comment_list = []

    for number, comment in enumerate(sorted_list_comments, start=1):
        comment_list.append((f"Рейтинг: {comment.find(class_=rating_find_alias).text}",
                             f"Комментарий: {comment.find(class_="tm-comment__body-content").text}"))

    result_dict = {
        "article_link": article_link,
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

    return result_dict


def parsing_one_article(searching_keyword, searching_filter="relevance"):
    """Функция для парсинга статьи"""

    url = f"https://habr.com/ru/search/?q={searching_keyword}&target_type=posts&order={searching_filter}"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }

    req = requests.get(url, headers=headers)
    src = req.text

    soup = BeautifulSoup(src, "lxml")

    # Проверяем если статьи по запросу
    no_articles = soup.find("div", class_="tm-empty-placeholder__text")
    if no_articles:
        return {"message": "По вашему запросы статьи не найдены"}

    # Находим первую статью
    first_article = soup.find("a", class_="tm-title__link")["href"]

    return parsing(first_article)


# print(parsing_one_article("django"))


def parsing_list_articles(searching_keyword, searching_filter="relevance"):
    """Функция для парсинга списка статьей"""

    url = f"https://habr.com/ru/search/?q={searching_keyword}&target_type=posts&order={searching_filter}"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }

    req = requests.get(url, headers=headers)
    src = req.text

    soup = BeautifulSoup(src, "lxml")

    # Проверяем если статьи по запросу
    no_articles = soup.find("div", class_="tm-empty-placeholder__text")
    if no_articles:
        return {"message": "По вашему запросы статьи не найдены"}

    # Находим все статьи
    find_articles = soup.find_all("article", class_="tm-articles-list__item")

    article_list = []

    for article in find_articles:
        # Находим статью
        article = article.find("a", class_="tm-title__link")["href"]
        article_list.append(parsing(article))

    return article_list


# pprint(parsing_list_articles_new("Python"))
# pprint(parsing_one_article("fsafsdfsadfs"))


from abc import ABC, abstractmethod


class ArticleParser(ABC):
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        }
        self.url = ''
        self.article_info = ''
        self.soup = ''
        self.soup_comments = ''
        self.searching_keyword = ''
        self.searching_filter = "relevance"
        self.search_result = ''
        self.amount = ''
        self.no_articles = False

    def start_parsing(self):
        self.get_url_searching()
        self.check_and_get_available_article()
        self.get_article_url()
        self.parsing_template()

    @abstractmethod
    def check_and_get_available_article(self, soup):
        pass

    @abstractmethod
    def get_article_url(self, url):
        pass

    def get_url_searching(self):
        url = f"https://habr.com/ru/search/?q={self.searching_keyword}&target_type=posts&order={self.searching_filter}"
        req = requests.get(url, headers=self.headers)
        src = req.text
        self.search_result = BeautifulSoup(src, "lxml")

    def parsing_template(self):
        if self.no_articles:
            return print(self.article_info)
        else:
            for article in self.article_info:
                req = requests.get(article["article_link"], headers=self.headers)
                src = req.text
                req_comments = requests.get(article["article_comments"], headers=self.headers)
                src_comments = req_comments.text
                soup = BeautifulSoup(src, "lxml")
                soup_comments = BeautifulSoup(src_comments, "lxml")

                article_title = soup.find(class_="tm-title tm-title_h1").text
                article_body = soup.find("div", id="post-content-body").get_text(strip=True)
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

                print(result_dict)


class ParsingOneArticle(ArticleParser):
    def __init__(self, searching_keyword='', searching_filter="relevance"):
        super().__init__()
        self.searching_keyword = searching_keyword
        self.searching_filter = searching_filter
        self.search_result = ''

    def check_and_get_available_article(self):
        no_articles = self.search_result.find("div", class_="tm-empty-placeholder__text")
        if no_articles:
            self.no_articles = True

        self.search_result = self.search_result.find("a", class_="tm-title__link")["href"]

    def get_article_url(self):
        self.article_info = []
        self.article_info.append(
            {"article_link": f"https://habr.com{self.search_result}",
             "article_comments": f"https://habr.com{self.search_result}comments/"}
        )


# a = ParsingOneArticle(searching_keyword="Python")
# a.start_parsing()


class ParsingListArticles(ArticleParser):
    def __init__(self, searching_keyword='', searching_filter="relevance"):
        super().__init__()
        self.searching_keyword = searching_keyword
        self.searching_filter = searching_filter

    def check_and_get_available_article(self):
        no_articles = self.search_result.find("div", class_="tm-empty-placeholder__text")
        if no_articles:
            self.no_articles = True
        self.search_result = self.search_result.find_all("article", class_="tm-articles-list__item")


    def get_article_url(self):
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



# a = ParsingListArticles(searching_keyword='dffsdfsafdsa')
# a.start_parsing()
