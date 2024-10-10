import enum

import requests
from celery.result import AsyncResult
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import status, generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import RegistrationForm, ParsingForm
from .models import Article, HistorySearch
from .parser_script import send_progress
from .serializers import (HistorySearchSerializer, ArticleDetailSerializer, ArticleSerializer, ParsingStatusSerializer,
                          UserSerializer)
from .tasks import start_parser, start_list_parser


class ParsingStates(enum.Enum):
    PENDING = "PENDING"
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"


def index(request):
    return HttpResponse("Hello World!")


class ParsingPageListSizeAPI(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class StartParsing(APIView):
    """Запускает парсинг статьи"""
    serializer_class = HistorySearchSerializer

    def post(self, request):
        serializer = HistorySearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        search_key = serializer.data["searching_key"]
        if serializer.data["parsing_options"] == "list":
            task = start_list_parser.delay(search_key, self.request.user.id, instance.id)
            send_progress(user_id=self.request.user.id, task_id=task.id, task_state=task.state,
                          type_message="parsing_status")
            return Response({"task_id": task.id}, status=status.HTTP_201_CREATED)
        elif serializer.data["parsing_options"] == "first":
            task = start_parser.delay(search_key, self.request.user.id, instance.id)
            send_progress(user_id=self.request.user.id, task_id=task.id, task_state=task.state,
                          type_message="parsing_status")
            return Response({"task_id": task.id}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        return instance


class ParsingStatusAPI(APIView):
    """Показывает статус парсинг запроса"""
    serializer_class = ParsingStatusSerializer

    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == ParsingStates.PENDING.value:
            return Response({"status": task.state}, status=status.HTTP_202_ACCEPTED)
        elif task.state == ParsingStates.FAILURE.value:
            return Response({"status": task.state}, status=status.HTTP_400_BAD_REQUEST)
        elif task.state == ParsingStates.SUCCESS.value:
            return Response({"status": task.state, "result_id": task.result}, status=status.HTTP_202_ACCEPTED)


class ParsingResult(APIView):
    """Показывает результат парсинга"""
    serializer_class = ArticleSerializer
    pagination_class = ParsingPageListSizeAPI

    def get(self, request, result_id):
        result = HistorySearch.objects.get(id=result_id)
        if result.parsing_options == "list":
            result = Article.objects.filter(search_id=result_id)
            return Response({"articles": ArticleSerializer(result, many=True).data})
        else:
            result = Article.objects.get(search_id=result_id)
            return Response({"article": ArticleSerializer(result).data})


class HistorySearchAPI(generics.ListAPIView):
    """Показывает историю запросов пользователя"""
    serializer_class = HistorySearchSerializer
    pagination_class = ParsingPageListSizeAPI
    queryset = HistorySearch.objects.all()

    def get_queryset(self):
        return HistorySearch.objects.filter(user=self.request.user)


class HistoryArticles(generics.ListAPIView):
    """Показывает историю запарсенных статей пользователем"""
    serializer_class = ArticleDetailSerializer
    pagination_class = ParsingPageListSizeAPI
    queryset = Article.objects.all()

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)


class DetailArticleViewAPI(generics.RetrieveAPIView):
    """Показывает конкретную статью"""
    serializer_class = ArticleDetailSerializer
    pagination_class = ParsingPageListSizeAPI

    def get_queryset(self):
        user = self.request.user
        return Article.objects.filter(user=user)


class UserSearchHistoryAPI(generics.RetrieveAPIView):
    """Показывает конкретный поисковый запрос пользователя"""
    serializer_class = HistorySearchSerializer
    pagination_class = ParsingPageListSizeAPI

    def get_queryset(self):
        user = self.request.user
        return HistorySearch.objects.filter(user=user)


class CreateUser(generics.CreateAPIView):
    """Создание пользователя"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class RegistrationUsersView(SuccessMessageMixin, generic.CreateView):
    """Регистрация на сайте"""

    form_class = RegistrationForm
    template_name = "registration.html"
    success_message = "Вы успешно зарегистрировались на сайте"
    success_url = reverse_lazy('index')
    extra_context = {"title": "Регистрация на сайте"}


class StartParsingView(generic.CreateView):
    """Запуск парсинга"""

    model = HistorySearch
    form_class = ParsingForm
    template_name = "parsing.html"
    next_page = "result.html"
    extra_context = {"title": "Запуск парсинга"}
    success_url = reverse_lazy('result')

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        self.object = form.save()

        api_url = "http://127.0.0.1:8000/api/v1/parsing/"
        params = {
            "searching_key": form.cleaned_data["searching_key"],
            "searching_filter": form.cleaned_data["searching_filter"],
            "parsing_options": form.cleaned_data["parsing_options"],
        }
        access_token = self.request.COOKIES.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        trigger = requests.post(api_url, json=params, headers=headers)
        response_data = trigger.json()
        task_id = response_data.get("task_id")
        self.request.session["task_id"] = task_id

        return super().form_valid(form)


class AuthorizationUserView(SuccessMessageMixin, LoginView):
    """Авторизация на сайте"""

    # form_class = AuthorizationForm
    template_name = "login.html"
    success_message = "Вы успешно вошли на сайт"
    next_page = "parsing"
    extra_context = {"title": "Авторизация"}

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response.set_cookie("access_token", access_token, httponly=True)
        response.set_cookie("refresh_token", refresh_token, httponly=True)
        self.request.session["access_token"] = access_token
        self.request.session["refresh_token"] = refresh_token
        return response


class LogOutUserView(SuccessMessageMixin, LogoutView):
    """Выход с аккаунта"""

    next_page = 'index'


class ResultParsingView(generic.ListView):
    """Результат парсинга"""

    model = HistorySearch
    template_name = "result.html"
    context_object_name = "articles"

    def get_queryset(self):
        query = HistorySearch.objects.filter(user_id=self.request.user).first()
        articles = Article.objects.filter(search_id=query.id)
        return articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.request.session.get("task_id")
        token = self.request.session.get("access_token")
        context["task_id"] = task_id
        context["token"] = token
        return context
