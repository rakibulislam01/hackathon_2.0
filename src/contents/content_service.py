import requests

from contents.models import Content, Tag, ContentTag, Author
from contents.serializers import ContentPostSerializer
from django.conf import settings

from contents.tasks import generate_comment


class ContentService:

    def generate_comment(self, content):
        """
        {
            "id": 1728113907,
            "timestamp": "2024-10-05T07:38:27.365469+00:00",
            "comment_text": "@jhon_doe Majority operation want up interview far cause Republican.",
            "content_id": 1
        }
        """
        url = "https://hackapi.hellozelf.com/api/v1/ai_comment/"
        headers = {"x-api-key": settings.X_API_KEY}
        payload = {
            "content_id": content.id,
            "title": content.title,
            "url": content.url,
            "author_username": content.author.name,
        }
        response = requests.post(url, data=payload, headers=headers)
        data = response.json()
        self.post_comment(content, data.get("comment_text"))

        return response

    def post_comment(self, content, comment_text):
        url = "https://hackapi.hellozelf.com/api/v1/comment/"
        headers = {"x-api-key": settings.X_API_KEY}
        payload = {"content_id": content.id, "comment_text": comment_text}
        response = requests.post(url, data=payload, headers=headers)
        return response

    def prepare_content(self, content_data):
        serializer = ContentPostSerializer(data=content_data, many=True)
        serializer.is_valid(raise_exception=True)
        contents = serializer.validated_data
        self.create_content(contents)

    def create_content(self, validated_data):
        contents = validated_data

        response_data = []

        for content in contents:
            author_object = self.get_or_create_author(content.get("author"))
            content_object, is_created = self.get_or_create_content(content, author_object)
            self.handle_tags(content.get("hashtags"), content_object)
            response_data.append(
                {
                    "content": content_object,
                    "author": content_object.author,
                }
            )
            if is_created:
                generate_comment(content_object)

    def get_or_create_author(self, author_data):
        instance, _ = Author.objects.update_or_create(
            unique_id=author_data["unique_external_id"],
            defaults={
                "unique_id": author_data["unique_external_id"],
                "username": author_data["unique_name"],
                "name": author_data["full_name"],
                "url": author_data["url"],
                "title": author_data["title"],
                "big_metadata": author_data["big_metadata"],
                "secret_value": author_data["secret_value"],
            },
        )
        return instance

    def get_or_create_content(self, content_data, author_object):

        instance, is_created = Content.objects.update_or_create(
            unique_id=content_data["unq_external_id"],
            defaults={
                "unique_id": content_data["unq_external_id"],
                "author": author_object,
                "title": content_data.get("title"),
                "big_metadata": content_data.get("big_metadata"),
                "secret_value": content_data.get("secret_value"),
                "thumbnail_url": content_data.get("thumbnail_view_url"),
                "like_count": content_data["stats"]["likes"],
                "comment_count": content_data["stats"]["comments"],
                "share_count": content_data["stats"]["shares"],
                "view_count": content_data["stats"]["views"],
            },
        )
        return instance, is_created

    def handle_tags(self, hashtags, content_object):
        for tag in hashtags:
            tag_object, created = Tag.objects.get_or_create(name=tag)
            ContentTag.objects.get_or_create(tag=tag_object, content=content_object)
