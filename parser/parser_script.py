import requests
from pprint import pprint
from bs4 import BeautifulSoup


def parsing_one_article(searching_keyword,searching_filter='relevance'):
    """Функция для парсинга статьи"""

    url = f'https://habr.com/ru/search/?q={searching_keyword}&target_type=posts&order={searching_filter}'


    headers = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }

    req = requests.get(url, headers=headers)
    src = req.text


    soup = BeautifulSoup(src, 'lxml')

    """Проверяем если статьи по запросу"""
    no_articles = soup.find('div',class_='tm-empty-placeholder__text')
    if no_articles:
        return {'message':'По вашему запросы статьи не найдены'}


    """Находим первую статью"""
    first_article = soup.find('a',class_='tm-title__link')['href']
    first_article_link = f"https://habr.com{first_article}"
    first_article_comments = f"https://habr.com{first_article}comments/"

    req = requests.get(first_article_link, headers=headers)
    src = req.text
    req_comments = requests.get(first_article_comments, headers=headers)
    src_comments = req_comments.text

    soup = BeautifulSoup(src, 'lxml')
    soup_comments = BeautifulSoup(src_comments, 'lxml')

    """ Нашли заголовок статьи"""
    article_title = soup.find(class_="tm-title tm-title_h1").text

    """Нашли текст статьи"""
    article_body = soup.find('div',id="post-content-body").get_text()

    """Автор статьи"""
    article_author = soup.find(class_="tm-user-info__username").text

    """Ссылка на автора статьи"""
    author_profile_link = soup.find(class_="tm-user-info__username")['href']
    article_author_profile = f"https://habr.com{author_profile_link}"

    """Дата публикации статьи"""
    article_date_raw = soup.find(class_="tm-article-datetime-published")
    article_date = article_date_raw.find("time")['title']

    """Рейтинг статьи"""
    article_rating = soup.find('span',class_="tm-votes-meter__value").text

    """Рейтинг автора статьи"""
    article_author_rating = soup.find(class_="tm-votes-lever__score-counter tm-votes-lever__score-counter_rating tm-votes-lever__score-counter").text

    """Количество добавления в закладки статьи"""
    article_bookmark = soup.find(class_="bookmarks-button__counter").text

    """Комментарии под статьей"""
    all_comments = soup_comments.find_all(class_="tm-comment-thread")
    rating_find_alias = "tm-votes-meter__value tm-votes-meter__value_positive tm-votes-meter__value_appearance-comment tm-votes-meter__value_rating tm-votes-meter__value"
    filtered_comments = [comment for comment in all_comments if comment.find(class_=rating_find_alias) is not None]
    sorted_list_comments = sorted(filtered_comments, key=lambda x: int(x.find(class_=rating_find_alias).text),reverse=True)

    if len(sorted_list_comments) > 5:
        sorted_list_comments = sorted_list_comments[:5]

    comment_list = []

    for number, comment in enumerate(sorted_list_comments, start=1):
        comment_list.append((f'Рейтинг: {comment.find(class_=rating_find_alias).text}', f'Комментарий: {comment.find(class_="tm-comment__body-content").text}'))



    result_dict = {
        'author_profile': article_author_profile,
        'author' : article_author,
        'author_rating' : article_author_rating,
        'title' : article_title,
        'content' : article_body,
        'date' : article_date,
        'rating' : article_rating,
        'bookmarks' : article_bookmark,
        'comments' : comment_list,
    }

    return result_dict



def parsing_article_list(searching_keyword, searching_filter='relevance'):
    """Функция для парсинга списка статей"""


    url = f'https://habr.com/ru/search/?q={searching_keyword}&target_type=posts&order={searching_filter}'

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }
    src = requests.get(url, headers=headers).text

    soup = BeautifulSoup(src, 'lxml')

    """Проверяем если статьи по запросу"""
    no_articles = soup.find('div',class_='tm-empty-placeholder__text')
    if no_articles:
        return {'message':'По вашему запросы статьи не найдены'}


    find_articles = soup.find_all('article',class_="tm-articles-list__item")

    data = []

    for article in find_articles:

        article_title = article.find(class_="tm-title__link").text

        article_link = article.find(class_="tm-title__link")['href']

        article_link = f"https://habr.com{article_link}"

        article_author = article.find(class_="tm-user-info__username").text

        article_author_link = article.find(class_="tm-user-info__username")['href']

        article_author_link = f"https://habr.com{article_author_link}"

        article_date = article.find(class_="tm-article-datetime-published").find("time")['title']

        article_body = article.find(class_="article-formatted-body").text

        article_rating = article.find("span", class_="tm-votes-meter__value").text

        article_bookmark = article.find(class_="bookmarks-button__counter").text

        all_comments = article.find(class_="tm-article-comments-counter-link__value").text

        result_dict = {
            'title' : article_title,
            'link' : article_link,
            'author' : article_author,
            'author_link' : article_author_link,
            'date' : article_date,
            'content' : article_body,
            'rating' : article_rating,
            'bookmarks' : article_bookmark,
            'comments' : all_comments,

        }
        data.append(result_dict)

    return data


# print(parsing_one_article('fast api'))
