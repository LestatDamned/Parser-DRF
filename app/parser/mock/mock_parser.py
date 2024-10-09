import requests

headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        }

searching_keyword = "django"
searching_filter = "relevance"

url = f"https://habr.com/ru/search/?q={searching_keyword}&target_type=posts&order={searching_filter}"

req = requests.get(url, headers=headers)

with open("mock_test_list_articles.html", "w") as file:
    file.write(req.text)

with open("articles.text", "w") as file:
    file.write(req.text)


url = "https://habr.com/ru/news/778430/"

req = requests.get(url, headers=headers)

with open("mock_test_article.html", "w") as file:
    file.write(req.text)

with open("article.text", "w") as file:
    file.write(req.text)


url = "https://habr.com/ru/news/778430/comments/"

req = requests.get(url, headers=headers)

with open("mock_test_article_comment.html", "w") as file:
    file.write(req.text)

with open("comments.text", "w") as file:
    file.write(req.text)