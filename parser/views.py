from celery.result import AsyncResult
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SearchArticles
from .parser_script import parsing_one_article, parsing_list_articles_new
from .serializers import SearchArticleSerializer, ArticleDetailSerializer
from .tasks import start_parser, start_list_parser


def index(request):
    return HttpResponse('Hello World!')

class ParsingResultAPI(APIView):

    def get_queryset(self,pk):
        query = get_object_or_404(SearchArticles, id=pk)
        return query


    def get(self,request,pk=None):
        query = self.get_queryset(pk)
        if query.parsing_options == 'list':
            task = start_list_parser.delay(query.searching_key)
            return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        else:
            task = start_parser.delay(query.searching_key)
            return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)



class SearchAPIViewSet(viewsets.ViewSet):
    serializer_class = SearchArticleSerializer

    def list(self, request):
        queryset = SearchArticles.objects.filter(user=request.user)
        serializer = SearchArticleSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ParsingStatusAPI(APIView):

    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            return Response({'status':task.state}, status=status.HTTP_202_ACCEPTED)
        elif task.state == 'SUCCESS':
            if task.result == {'message': 'По вашему запросы статьи не найдены'}:
                return Response(task.result, status=status.HTTP_200_OK)
            return Response(ArticleDetailSerializer(task.result, many=True).data, status=status.HTTP_200_OK)
