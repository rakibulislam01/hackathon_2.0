from django.db import models

from contents.models.models import BaseModel


class VideoPublisher(BaseModel):
    following = models.BigIntegerField(default=0)
    followers = models.BigIntegerField(default=0)
    likes = models.BigIntegerField(default=0)
    user_name = models.CharField(max_length=256, primary_key=True)

    def _str_(self) -> str:
        return self.user_name


class VideoData(BaseModel):
    video_url = models.URLField(null=True, blank=True)
    video_caption = models.TextField(null=True, blank=True)
    video_publisher = models.ForeignKey(VideoPublisher, on_delete=models.DO_NOTHING, null=True, blank=True)

    query = models.TextField(null=True, blank=True)

    def _str_(self) -> str:
        return self.video_caption
