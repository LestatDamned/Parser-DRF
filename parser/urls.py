from django.urls import path
from .views import *



urlpatterns = [
    path('', index, name='index'),
    path('api/v1/status/<str:task_id>/',ParsingStatusAPI.as_view(), name='status-api-search'),
    path('api/v1/parsing/', StartParsing.as_view(), name='parsing-api-search'),
    path('api/v1/result/<int:result_id>/',ParsingResult.as_view(), name='result-api-search'),
    path('api/v1/history/searches/', HistorySearchAPI.as_view(), name='history-search-api'),
    path('api/v1/history/articles/', HistoryArticles.as_view(), name='history-articles-api'),

]
