from contents.models import Content, Tag, ContentTag, Author


class ContentService:

    def create_content(self, validated_data):
        contents = validated_data

        response_data = []

        for content in contents:
            author_object = self.get_or_create_author(content.get("author"))
            content_object = self.get_or_create_content(content, author_object)
            self.handle_tags(content.get("hashtags"), content_object)
            response_data.append(
                {
                    "content": content_object,
                    "author": content_object.author,
                }
            )

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

        instance, _ = Content.objects.update_or_create(
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
        return instance

    def handle_tags(self, hashtags, content_object):
        for tag in hashtags:
            tag_object, created = Tag.objects.get_or_create(name=tag)
            ContentTag.objects.get_or_create(tag=tag_object, content=content_object)
