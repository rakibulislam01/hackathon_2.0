import json

import requests
from django.db.models import Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from contents.content_service import ContentService
from contents.filters import ContentFilter, VideoFilter
from contents.models import Content, Author
from contents.models.video_data import VideoData
from contents.serializers import (
    ContentSerializer,
    ContentPostSerializer,
    VideoDataSerializer,
    VideoPublisher,
    VideoPublisherSerializer,
)
from .serializers import VideoListSerializer, VideoDetailSerializer


class ContentAPIView(APIView):
    pagination_class = LimitOffsetPagination
    filterset_class = ContentFilter
    service = ContentService()

    def get_queryset(self):
        queryset = Content.objects.all().select_related("author")
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs

    def get(self, request):
        """
        TODO: Client is complaining about the app performance, the app is loading very slowly, our QA identified that
         this api is slow af. Make the api performant. Need to add pagination. But cannot use rest framework view set.
         As frontend, app team already using this api, do not change the api schema.
         Need to send some additional data as well,
         --------------------------------
         1. Total Engagement = like_count + comment_count + share_count
         2. Engagement Rate = Total Engagement / Views
         Users are complaining these additional data is wrong.
         Need filter support for client side. Add filters for (author_id, author_username, timeframe )
         For timeframe, the content's timestamp must be withing 'x' days.
         Example: api_url?timeframe=7, will get contents that has timestamp now - '7' days
         --------------------------------
         So things to do:
         1. Make the api performant
         2. Fix the additional data point in the schema
            - Total Engagement = like_count + comment_count + share_count
            - Engagement Rate = Total Engagement / Views
            - Tags: List of tags connected with the content
         3. Filter Support for client side
            - author_id: Author's db id
            - author_username: Author's username
            - timeframe: Content that has timestamp: now - 'x' days
            - tag_id: Tag ID
            - title (insensitive match IE: SQL `ilike %text%`)
         4. Must not change the inner api schema
         5. Remove metadata and secret value from schema
         6. Add pagination
            - Should have page number pagination
            - Should have items per page support in query params
            Example: `api_url?items_per_page=10&page=2`
        """
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        data_list = []
        for query in queryset:
            author = Author.objects.get(id=query.author_id)
            data = {"content": query, "author": author}
            data_list.append(data)
        serialized = ContentSerializer(data_list, many=True)
        paginator.get_paginated_response(serialized.data)
        return paginator.get_paginated_response(serialized.data)

    def post(self, request):
        """
        TODO: This api is very hard to read, and inefficient.
         The users complaining that the contents they are seeing is not being updated.
         Please find out, why the stats are not being updated.
         ------------------
         Things to change:
         1. This api is hard to read, not developer friendly
         2. Support list, make this api accept list of objects and save it
         3. Fix the users complain
        """

        serializer = ContentPostSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        contents = serializer.validated_data
        response_data = self.service.create_content(contents)
        return Response(ContentSerializer(response_data, many=True).data)


class ContentStatsAPIView(APIView):
    filterset_class = ContentFilter

    def get_queryset(self):
        queryset = Content.objects.all()
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs

    """
    TODO: This api is taking way too much time to resolve.
     Contents that will be fetched using `ContentAPIView`, we need stats for that
     So it must have the same filters as `ContentAPIView`
     Filter Support for client side
            - author_id: Author's db id
            - author_username: Author's username
            - timeframe: Content that has timestamp: now - 'x' days
            - tag_id: Tag ID
            - title (insensitive match IE: SQL `ilike %text%`)
     -------------------------
     Things To do:
     1. Make the api performant
     2. Fix the additional data point (IE: total engagement, total engagement rate)
     3. Filter Support for client side
         - author_id: Author's db id
         - author_id: Author's db id
         - author_username: Author's username
         - timeframe: Content that has timestamp: now - 'x' days
         - tag_id: Tag ID
         - title (insensitive match IE: SQL `ilike %text%`)
     --------------------------
     Bonus: What changes do we need if we want timezone support?
    """

    def get(self, request):
        queryset = self.get_queryset()
        data = {
            "total_likes": 0,
            "total_shares": 0,
            "total_views": 0,
            "total_comments": 0,
            "total_engagement": 0,
            "total_engagement_rate": 0,
            "total_contents": 0,
            "total_followers": 0,
        }
        aggregated_data = queryset.aggregate(
            total_likes=Sum("like_count"),
            total_shares=Sum("share_count"),
            total_views=Sum("view_count"),
            total_comments=Sum("comment_count"),
            total_followers=Sum("author__followers"),
            total_contents=Count("id"),
        )

        data.update(aggregated_data)
        data["total_engagement"] = data["total_likes"] + data["total_shares"] + data["total_comments"]
        data["total_engagement_rate"] = (
            (data["total_engagement"] / data["total_views"]) * 100 if data["total_views"] else 0
        )
        return Response(data, status=status.HTTP_201_CREATED)


class VideoDataAPIView(APIView):
    serializer_class = VideoDataSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            user_name = data.get("video_publisher", None)
            print(f"User Name: {user_name}")
            if user_name:
                video_publisher, _ = VideoPublisher.objects.get_or_create(user_name=user_name)
            else:
                video_publisher = None
            content, _ = VideoData.objects.update_or_create(
                video_url=data.get("video_url"),
                defaults={
                    "video_url": data.get("video_url"),
                    "video_caption": data.get("video_caption"),
                    "video_publisher": video_publisher,
                    "query": data.get("query"),
                },
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VideoPublisherAPIView(APIView):
    serializer_class = VideoPublisherSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            content, _ = VideoPublisher.objects.update_or_create(
                user_name=data.get("user_name"),
                defaults={
                    "user_name": data.get("user_name"),
                    "following": data.get("following"),
                    "followers": data.get("followers"),
                    "likes": data.get("likes"),
                },
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Custom pagination class to control the number of items per page
class VideoPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 100


class VideoListView(ListAPIView):
    queryset = VideoData.objects.select_related("video_publisher").all()
    serializer_class = VideoListSerializer
    pagination_class = VideoPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # Define available filters
    filterset_class = VideoFilter

    # Sorting options (follower count and likes)
    ordering_fields = ["video_publisher__followers", "video_publisher__likes"]
    ordering = ["video_publisher__followers"]  # Default ordering by followers

    def get_queryset(self):
        """
        Override get_queryset to allow dynamic filtering and sorting.
        This method ensures efficient database queries.
        """
        queryset = super().get_queryset()
        return queryset


class VideoDetailView(RetrieveAPIView):
    queryset = VideoData.objects.select_related("video_publisher")  # optimized query
    serializer_class = VideoDetailSerializer
    lookup_field = "id"


class VideoHashtagDataAPIView(APIView):
    def get(self, request):
        data = request.query_params.dict()
        hash_tag = data.get("hashtag")
        if not hash_tag:
            return Response({"error": "Missing hashtag"}, status=status.HTTP_400_BAD_REQUEST)
        base_url = "http://192.168.243.159:3000/scrapingquery/"
        payload = json.dumps({"query": "beautiful destination"})
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", base_url, headers=headers, data=payload)

        return Response(response.json(), status=response.status_code)
