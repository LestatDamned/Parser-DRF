from celery.result import AsyncResult
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, HistorySearch
from .serializers import HistorySearchSerializer, ArticleDetailSerializer, ArticleSerializer
from .tasks import start_parser, start_list_parser


def index(request):
    return HttpResponse('Hello World!')


class ParsingStatusAPI(APIView):

    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            return Response({'status':task.state}, status=status.HTTP_202_ACCEPTED)
        elif task.state == 'SUCCESS':

            return Response({'status':task.state, "result_id": task.result}, status=status.HTTP_202_ACCEPTED)


class StartParsing(APIView):
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


class ParsingResult(APIView):

    def get(self, request, result_id):
        result = HistorySearch.objects.get(id=result_id)
        if result.parsing_options == 'list':
            result = Article.objects.filter(search_id=result_id)
            return Response({"articles": ArticleSerializer(result, many=True).data})
        return Response({"article": ArticleSerializer(result).data})


class HistorySearchAPI(APIView):
    def get(self,request):
        result_list = HistorySearch.objects.filter(user=request.user)
        return Response({"searching_history": HistorySearchSerializer(result_list,many=True).data})

class HistoryArticles(APIView):
    def get(self,request):
        result_list = Article.objects.filter(user=request.user)
        return Response({"articles": ArticleDetailSerializer(result_list,many=True).data})