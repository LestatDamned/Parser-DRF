from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, SearchArticles
from .parser_script import parsing_one_article, parsing_article_list
from .serializers import SearchArticleSerializer


def index(request):
    return HttpResponse('Hello World!')

class ParsingResultAPI(APIView):

    def get_queryset(self,pk):
        query = get_object_or_404(SearchArticles, id=pk)
        return query


    def get(self,request,pk=None):
        query = self.get_queryset(pk)
        if query.parsing_options == 'list':
            result = parsing_article_list(query.searching_key)
            return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = parsing_one_article(query.searching_key)
            return Response(data=result, status=status.HTTP_200_OK)



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