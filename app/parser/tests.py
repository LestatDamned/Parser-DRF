import os.path
from unittest.mock import patch, Mock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from parser.models import HistorySearch, Article
from parser.parser_script import ParsingOneArticle
from parser.serializers import ArticleSerializer, HistorySearchSerializer, ArticleDetailSerializer
from parser.views import ParsingStates


class ParsingStatusAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)

    @patch("parser.views.AsyncResult")
    def test_get_parsing_status_pending(self, mock_async_result):
        task_id = "test_task_id"
        mock_task = mock_async_result.return_value
        mock_task.state = ParsingStates.PENDING.value

        response = self.client.get(reverse("status_parsing", kwargs={"task_id": task_id}))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data, {"status": mock_task.state})

    @patch("parser.views.AsyncResult")
    def test_get_parsing_status_failure(self, mock_async_result):
        task_id = "test_task_id"
        mock_task = mock_async_result.return_value
        mock_task.state = ParsingStates.FAILURE.value

        response = self.client.get(reverse("status_parsing", kwargs={"task_id": task_id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"status": mock_task.state})

    @patch("parser.views.AsyncResult")
    def test_get_parsing_status_success(self, mock_async_result):
        task_id = "test_task_id"
        mock_task = mock_async_result.return_value
        mock_task.state = ParsingStates.SUCCESS.value
        mock_task.result = "result_id"

        response = self.client.get(reverse("status_parsing", kwargs={"task_id": task_id}))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data, {"status": mock_task.state, "result_id": mock_task.result})


from django.contrib.auth.models import User


class ParsingResultAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)
        self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                           searching_filter="relevance", parsing_options="first")
        self.second_history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                                  searching_filter="relevance", parsing_options="list")
        self.article = Article.objects.create(user=self.user_test, search_id=self.history_search,
                                              title="Django Article", content="Django Content")
        self.second_article = Article.objects.create(user=self.user_test, search_id=self.second_history_search,
                                                     title="Python Article", content="Python Content1")
        self.third_article = Article.objects.create(user=self.user_test, search_id=self.second_history_search,
                                                    title="Python Article2", content="Python Content2")

    def test_parsing_result(self):
        url = reverse("parsing_result", kwargs={"result_id": self.history_search.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"article": ArticleSerializer(self.article).data})

    def test_parsing_result_list(self):
        url = reverse("parsing_result", kwargs={"result_id": self.second_history_search.id})

        response = self.client.get(url)
        result = Article.objects.filter(search_id=self.second_history_search)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"articles": ArticleSerializer(result, many=True).data})


from django.urls import reverse


class HistorySearchAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)
        self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                           searching_filter="relevance", parsing_options="first")

    def test_history_search(self):
        url = reverse("parsing_history")
        response = self.client.get(url)
        result = HistorySearch.objects.filter(id=self.history_search.id)
        expected_data = {
            "count": result.count(),
            "next": None,
            "previous": None,
            "results": HistorySearchSerializer(result, many=True).data
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)


from rest_framework.test import APITestCase


class HistoryArticleAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)
        self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                           searching_filter="relevance", parsing_options="first")

    def test_history_article(self):
        url = reverse("parsing_articles")
        response = self.client.get(url)
        result = Article.objects.filter(user=self.user_test)
        expected_data = {
            "count": result.count(),
            "next": None,
            "previous": None,
            "results": ArticleDetailSerializer(result, many=True).data
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)


class DetailArticleAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)
        self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                           searching_filter="relevance", parsing_options="first")
        self.article = Article.objects.create(user=self.user_test, search_id=self.history_search,
                                              title="Django Article", content="Django Content")

    def test_detail_article(self):
        url = reverse("detail_article", kwargs={"pk": self.article.id})
        response = self.client.get(url)
        result = Article.objects.get(id=self.article.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ArticleDetailSerializer(result).data)


class DetailHistoryAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)
        self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                           searching_filter="relevance", parsing_options="first")
        self.article = Article.objects.create(user=self.user_test, search_id=self.history_search,
                                              title="Django Article", content="Django Content")

    def test_detail_history(self):
        url = reverse("detail_history", kwargs={"pk": self.history_search.id})
        response = self.client.get(url)
        result = HistorySearch.objects.filter(user_id=self.user_test.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([response.data], HistorySearchSerializer(result, many=True).data)


class CreateUserAPITestCase(APITestCase):
    def test_create_user(self):
        url = reverse("create_user")
        data = {"username": "test", "password": "12345", "email": "test@test.ru"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)


class JWTauthenticationAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()

    def test_authenticate(self):
        url = reverse("token_obtain_pair")
        data = {"username": self.user_test.username, "password": "12345"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"])


class PasringClassTestCase(TestCase):
    def setUp(self):
        self.parser = ParsingOneArticle(searching_keyword="Python", user_id=1)
        self.mock_folder = os.path.join(os.path.dirname(__file__), 'mock')

    @patch('requests.get')
    def test_parsing_one_article(self, mock_get):
        with open(os.path.join(self.mock_folder, 'mock_test_list_articles.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()

        with open(os.path.join(self.mock_folder, 'mock_test_article.html'), 'r', encoding='utf-8') as f:
            html_content2 = f.read()

        with open(os.path.join(self.mock_folder, 'mock_test_article_comment.html'), 'r', encoding='utf-8') as f:
            html_content3 = f.read()

        mock_get.side_effect = [
            Mock(text=html_content),
            Mock(text=html_content2),
            Mock(text=html_content3),
        ]

        result = self.parser.start_parsing()
        print(result)

#
#
# class ParsingClassTestCase(TestCase):
#     def setUp(self):
#         self.user_id = 1
#         self.parser = ParsingOneArticle(searching_keyword="django", user_id=self.user_id)
#         self.mock_folder = os.path.join(os.path.dirname(__file__), "mock")
#
#     def get_mock_html(self, filename):
#         with open(os.path.join(self.mock_folder, filename), 'r', encoding='utf-8') as f:
#             return f.read()
#
#     @patch("parser.parser_script.send_progress")
#     @patch("parser.parser_script.ParsingOneArticle")
#     @patch("parser.parser_script.requests.get")
#     def test_parsing_one_article(self, mock_parsing_one_article, mock_send_progress, mock_get):
#         mock_get = MagicMock()
#         mock_get.return_value.text = os.path.join(os.path.dirname(self.mock_folder),"mock_test_list_articles.html")
#         # mock_get.return_value = self.get_mock_html("mock_test_article.html")
#         # mock_get.return_value = self.get_mock_html("mock_test_article_comment.html")
#
#
#
#         result = self.parser.start_parsing()
#         print(result)


#
# class StartParsingAPITestCase(APITestCase):
#     def setUp(self):
#         self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
#         self.user_test.set_password("12345")
#         self.user_test.save()
#         self.client.force_authenticate(user=self.user_test)
#
#         self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
#                                                            searching_filter="relevance", parsing_options="first")
#         self.history_search_list = HistorySearch.objects.create(user=self.user_test, searching_key="django",
#                                                                 searching_filter="relevance",
#                                                                 parsing_options="list")
#
    # @patch("parser.tasks.start_parser")
    # def test_start_parsing(self, mock_start_parser):
    #     mock_task = mock_start_parser.return_value
    #     mock_task.id = "test_task_id"
    #
    #
    #     url = reverse("start_parsing")
    #     data = {
    #         "searching_key": "test-key",
    #         "parsing_options": "first",
    #
    #     }
    #
    #     response = self.client.post(url, data, format="json")
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data, {"task_id": "test_task_id"})

    # @patch("parser.views.start_list_parser")
    # def test_start_list_parser(self,mock_start_list_parser):
    #     mock_task = mock_start_list_parser.return_value
    #     mock_task.task_id = "test_task_id"
    #
    #     url = reverse("start_parsing")
    #     response = self.client.post(url, {"user": self.history_search.user.id,
    #                                      "searching_key": self.history_search.searching_key,
    #                                      "searching_filter": self.history_search.searching_filter,
    #                                      "parsing_options": self.history_search.parsing_options})
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data, {"task_id": "test_task_id"})
    #
