from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from parser.models import HistorySearch, Article
from parser.serializers import ArticleSerializer, HistorySearchSerializer, ArticleDetailSerializer


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
        mock_task.state = "PENDING"

        response = self.client.get(reverse("status_parsing", kwargs={"task_id": task_id}))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data, {"status": "PENDING"})

    @patch("parser.views.AsyncResult")
    def test_get_parsing_status_failure(self, mock_async_result):
        task_id = "test_task_id"
        mock_task = mock_async_result.return_value
        mock_task.state = "FAILURE"

        response = self.client.get(reverse("status_parsing", kwargs={"task_id": task_id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"status": "FAILURE"})

    @patch("parser.views.AsyncResult")
    def test_get_parsing_status_success(self, mock_async_result):
        task_id = "test_task_id"
        mock_task = mock_async_result.return_value
        mock_task.state = "SUCCESS"
        mock_task.result = "result_id"

        response = self.client.get(reverse("status_parsing", kwargs={"task_id": task_id}))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data, {"status": "SUCCESS", "result_id": "result_id"})


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

    # def test_detail_history(self):
    #     url = reverse("detail_history", kwargs={"pk": self.history_search.id})
    #     response = self.client.get(url)
    #     result = HistorySearch.objects.filter(id=self.history_search.id)
    #     # self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     print(HistorySearchSerializer(result).data)
    #     # self.assertEqual(response.data, HistorySearchSerializer(result).data)


class CreateUserAPITestCase(APITestCase):
    def test_create_user(self):
        url = reverse("create_user")
        data = {"username": "test", "password": "12345"}
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


class StartParsingAPITestCase(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
        self.user_test.set_password("12345")
        self.user_test.save()
        self.client.force_authenticate(user=self.user_test)

        self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                           searching_filter="relevance", parsing_options="first")
        self.history_search_list = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                                searching_filter="relevance",
                                                                parsing_options="list")

    # @patch("parser.views.start_parser.delay")
    # def test_start_parsing(self, mock_start_parser):
    #     mock_task = mock_start_parser.return_value
    #     mock_task.task_id = "test_task_id"
    #
    #
    #     url = reverse("start_parsing")
    #     data = {
    #         "searching_key": "test-key",
    #         "parsing_options": "first"
    #     }
    #
    #     response = self.client.post(url, data, format="json")
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data, {"task_id": "test_task_id"})
    #
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

#     # class ParserTest(APITestCase):
#     def setUp(self):
#         self.user_test = User.objects.create(username="dabapps", email="dabapps@mail.ru")
#         self.user_test.set_password("12345")
#         self.user_test.save()
#
#         self.history_search = HistorySearch.objects.create(user=self.user_test, searching_key="django",
#                                                             searching_filter="relevance", parsing_options="first")
#
#
#         self.test_article = Article.objects.create(user=self.user_test, search_id=self.history_search,
#                                               title="Test Article", content="Test Content")
#
#
#     def authenticate(self):
#         # Получение JWT токена
#         url = reverse("token_obtain_pair")
#         data = {"username": self.user_test.username, "password": "12345"}
#         response = self.client.post(url, data, format="json")
#         self.token = response.data["access"]
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
#
#
#     def parsing(self):
#         self.authenticate()
#         url = reverse("start_parsing")
#         req = self.client.post(url, {"user": self.history_search.user.id,
#                                      "searching_key": self.history_search.searching_key,
#                                      "searching_filter": self.history_search.searching_filter,
#                                      "parsing_options": self.history_search.parsing_options})
#         return req
#
#     def parsing_status(self):
#         req = self.parsing()
#         task_id = req.data["task_id"]
#
#         url = reverse("status_parsing", kwargs={"task_id": task_id})
#         req = self.client.get(url, format="json")
#         return req.data["result_id"]
#
#
#
#     def test_start_parsing(self):
#         req = self.parsing()
#
#         self.assertEqual(req.status_code, status.HTTP_202_ACCEPTED)
#         self.assertTrue(req.data["task_id"])
#
#     def test_status_parsing(self):
#         req = self.parsing()
#         task_id = req.data["task_id"]
#
#         url = reverse("status_parsing", kwargs={"task_id": task_id})
#         req = self.client.get(url, format="json")
#         self.assertEqual(req.status_code, status.HTTP_202_ACCEPTED)
#
#
#
#     def test_parsing_result(self):
#         result_id = self.parsing_status()
#
#         url = reverse("parsing_result", kwargs={"result_id": result_id})
#         req = self.client.get(url, format="json")
#         self.assertEqual(req.status_code, status.HTTP_200_OK)
#         print(req.data)
#
#
#
#
#     def test_history_parsing(self):
#         self.authenticate()
#         url = reverse("parsing_history")
#         req = self.client.get(url, format="json")
#         self.assertEqual(req.status_code, status.HTTP_200_OK)
#

# url = reverse("parsing_articles")
# req = self.client.get(url,format="json")
# self.assertEqual(req.status_code, status.HTTP_200_OK)


# def test_start_parsing(self):
#     self.authenticate()
#
#     # Тестирование начала парсинга
#     url = reverse("start_parsing")
#     req = self.client.post(url, {"user": self.history_search.user.id,
#                                  "searching_key": self.history_search.searching_key,
#                                  "searching_filter": self.history_search.searching_filter,
#                                  "parsing_options": self.history_search.parsing_options})
#     self.assertEqual(req.status_code, status.HTTP_202_ACCEPTED)
#     self.assertTrue(req.data["task_id"])


# def test_status_parsing(self):
#     self.authenticate()
#     url = reverse("start_parsing")
#     req = self.client.post(url, {"user": self.history_search.user.id,
#                                  "searching_key": self.history_search.searching_key,
#                                  "searching_filter": self.history_search.searching_filter,
#                                  "parsing_options": self.history_search.parsing_options})
#     print(req.data)
#     self.task_id = req.data["task_id"]
#
#     url = reverse("status_parsing", kwargs={"task_id": self.task_id})
#     req = self.client.get(url, format="json")
#     self.assertEqual(req.status_code, status.HTTP_202_ACCEPTED)
#     print(req.data)
#     url = reverse("status_parsing", kwargs={"task_id": self.task_id})
#     req = self.client.get(url, format="json")
#     print(req.data)
#
