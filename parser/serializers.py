from rest_framework import serializers

from .models import OneArticle, SearchArticles



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


