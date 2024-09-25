from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from parser.models import HistorySearch


class ParserTest(APITestCase):
    def setUp(self):
        self.user_test = User.objects.create(username='dabapps', email='dabapps@mail.ru')
        self.user_test.set_password('12345')
        self.user_test.save()

        self.parsing_request = HistorySearch.objects.create(user=self.user_test, searching_key="django",
                                                            searching_filter="relevance", parsing_options='first')

    def test_start_parsing(self):
        # Получение JWT токена
        url = reverse('token_obtain_pair')
        data = {'username': self.user_test.username, 'password': '12345'}
        response = self.client.post(url, data, format='json')
        # print(response.data)
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Тестирование начала парсинга
        url = reverse('start_parsing')
        req = self.client.post(url, {'user': self.parsing_request.user.id,
                                     'searching_key': self.parsing_request.searching_key,
                                     'searching_filter': self.parsing_request.searching_filter,
                                     'parsing_options': self.parsing_request.parsing_options})
        self.assertEqual(req.status_code, status.HTTP_202_ACCEPTED)



# class AccountTests(APITestCase):
#     def test_create_account(self):
#         """
#         Проверяем что можем создавать нового пользователя.
#         """
#         url = reverse('create_user')
#         data = {'username': 'DabApps', 'email': 'dabapps@mail.ru', 'password': '12345'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(User.objects.count(), 1)
#         self.assertEqual(User.objects.get().username, 'DabApps')
#

# class StartParsingTests(APITestCase):
#     def setUp(self):
#         HistorySearch.objects.create(user=1,searching_key="django",searching_filter="relevance",parsing_options='first')
#         # HistorySearch.objects.create(user=2,searching_key="python",searching_filter="date",parsing_options='list')
#
#     def test_start_parsing(self):
#         url = reverse('start_parsing')
#         data1 = HistorySearch.objects.get(user=1)
#         # data2 = HistorySearch.objects.get(user=2)
#         response = self.client.post(url, data1, format='json')
#         self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
#         self.assertEqual(response.data['task_id'],1)
#         self.assertEqual(HistorySearch.objects.get(user=1).searching_key, 'django')
