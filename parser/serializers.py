from rest_framework import serializers

from .models import Article, OneArticle, SearchArticles


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class ArticleListSerializer(serializers.Serializer):
    title = serializers.CharField()
    link = serializers.URLField()
    author = serializers.CharField()
    author_link = serializers.URLField()
    date = serializers.CharField()
    content = serializers.CharField()
    rating = serializers.CharField()
    bookmarks = serializers.CharField()
    comments = serializers.CharField()


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneArticle
        fields = '__all__'


class SearchArticleSerializer(serializers.ModelSerializer):
    # user = serializers.Field(source='user.id')
    class Meta:
        model = SearchArticles
        fields = ('id','user','searching_key','searching_filter','parsing_options')
        read_only_fields = ('user',)


