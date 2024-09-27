from django.urls import path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("api/v1/create_user/", CreateUser.as_view(), name="create_user"),
    path("api/v1/parsing/", StartParsing.as_view(), name="start_parsing"),
    path("api/v1/parsing/status/<str:task_id>/", ParsingStatusAPI.as_view(), name="status_parsing"),
    path("api/v1/parsing/result/<int:result_id>/", ParsingResult.as_view(), name="parsing_result"),
    path("api/v1/history/searches/", HistorySearchAPI.as_view(), name="parsing_history"),
    path("api/v1/history/articles/", HistoryArticles.as_view(), name="parsing_articles"),
    path("api/v1/history/article/<int:pk>/", DetailArticleViewAPI.as_view(), name="detail_article"),
    path("api/v1/history/search/<int:pk>/", UserSearchHistoryAPI.as_view(), name="detail_history"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),

]
