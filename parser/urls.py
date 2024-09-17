from django.urls import path
from .views import *



urlpatterns = [
    path('', index, name='index'),
    # path('api/v1/article_test', ArticleAPIListView.as_view(), name='article-api-list'),
    # path('api/v1/article_list/', ArticleSearchAPIView.as_view(), name='article-api-search'),
    # path('api/v1/article/', ArticleSearchFirstAPIView.as_view(), name='article-api-search-first'),
    path('api/v1/result/<int:pk>/',ParsingResultAPI.as_view(), name='result-api-search'),
    path('api/v1/status/<str:task_id>/',ParsingStatusAPI.as_view(), name='status-api-search'),

]
