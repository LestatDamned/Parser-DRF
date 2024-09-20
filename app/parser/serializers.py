from rest_framework import serializers

from .models import Article, HistorySearch



class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("article_link", "title", "author_profile", "author", "author_rating", "content", "date", "rating",
                  "bookmarks","comments")

    def create(self, validated_data):
        return Article.objects.create(**validated_data)



class HistorySearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorySearch
        fields = ('id','user','searching_key','searching_filter','parsing_options')
        read_only_fields = ('user',)


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("id", "search_id", "article_link", "title", "author_profile", "author", "author_rating", "content", "date",
                  "rating", "bookmarks","comments")

    def create(self, validated_data):
        return Article.objects.create(**validated_data)



class ParsingStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    result_id = serializers.CharField(required=False)