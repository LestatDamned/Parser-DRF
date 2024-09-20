from django.urls import path, re_path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('api/v1/parsing/', StartParsing.as_view(), name='parsing-api-search'),
    path('api/v1/parsing/status/<str:task_id>/',ParsingStatusAPI.as_view(), name='status-api-search'),
    path('api/v1/parsing/result/<int:result_id>/',ParsingResult.as_view(), name='result-api-search'),
    path('api/v1/history/searches/', HistorySearchAPI.as_view(), name='history-search-api'),
    path('api/v1/history/articles/', HistoryArticles.as_view(), name='history-articles-api'),
    path('api/v1/history/article/<int:pk>/', DetailArticleViewAPI.as_view(), name='user-search-article-api'),
    path('api/v1/history/search/<int:pk>/', UserSearchHistoryAPI.as_view(), name='user-search-api'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),

]
