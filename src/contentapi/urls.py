from django.contrib import admin
from django.urls import path

from contents.views import (
    ContentAPIView,
    ContentStatsAPIView,
    VideoDataAPIView,
    VideoListView,
    VideoDetailView,
    VideoHashtagDataAPIView,
    VideoPublisherAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/contents/stats/", ContentStatsAPIView.as_view(), name="api-contents-stats"),
    path("api/contents/", ContentAPIView.as_view(), name="api-contents"),
    path("api/video-data/", VideoDataAPIView.as_view(), name="video-data"),
    path("api/video-publisher/", VideoPublisherAPIView.as_view(), name="video-publisher"),
    path("api/video-data/all/", VideoListView.as_view(), name="video-list"),
    path("api/video-data/<int:id>/", VideoDetailView.as_view(), name="video-detail"),
    path("api/hash-tag/", VideoHashtagDataAPIView.as_view(), name="hash-tag"),
]
