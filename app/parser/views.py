from celery.result import AsyncResult
from django.http import HttpResponse
from rest_framework import status, generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, HistorySearch
from .serializers import (HistorySearchSerializer, ArticleDetailSerializer, ArticleSerializer, ParsingStatusSerializer,
                          UserSerializer)
from .tasks import start_parser, start_list_parser


def index(request):
    return HttpResponse('Hello World!')



class ParsingPageListSizeAPI(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class StartParsing(APIView):
    """Запускает парсинг статьи"""
    serializer_class = HistorySearchSerializer

    def post(self, request):
        serializer = HistorySearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        search_key = serializer.data['searching_key']
        if serializer.data['parsing_options'] == 'list':
            task = start_list_parser.delay(search_key,self.request.user.id,instance.id)
            return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        elif serializer.data['parsing_options'] == 'first':
            task = start_parser.delay(search_key,self.request.user.id,instance.id)
            return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        return instance



class ParsingStatusAPI(APIView):
    """Показывает статус парсинг запроса"""
    serializer_class = ParsingStatusSerializer
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            return Response({'status':task.state}, status=status.HTTP_202_ACCEPTED)
        elif task.state == 'FAILURE':
            return Response({'status':task.state}, status=status.HTTP_400_BAD_REQUEST)
        elif task.state == 'SUCCESS':
            return Response({'status':task.state, "result_id": task.result}, status=status.HTTP_202_ACCEPTED)



class ParsingResult(APIView):
    """Показывает результат парсинга"""
    serializer_class = ArticleSerializer
    pagination_class = ParsingPageListSizeAPI

    def get(self, request, result_id):
        result = HistorySearch.objects.get(id=result_id)
        if result.parsing_options == 'list':
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
