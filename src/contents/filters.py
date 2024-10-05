from django_filters import rest_framework as filters
from django.db.models import Q
from datetime import datetime, timedelta


class ContentFilter(filters.FilterSet):
    author_id = filters.CharFilter(field_name="author__id", lookup_expr="icontains")
    author_username = filters.CharFilter(field_name="author__username", lookup_expr="icontains")
    timeframe = filters.CharFilter(method="filter_by_timeframe")
    tag_id = filters.CharFilter(method="filter_by_tag")
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")

    def filter_by_tag(self, queryset, name, value):
        if value is None:
            return queryset
        queryset = queryset.filter(contenttag__tag__id=value).order_by("-id")
        return queryset

    def filter_by_timeframe(self, queryset, name, value):
        if value is None:
            return queryset
        try:
            days = int(value)
        except ValueError:
            return queryset
        date = datetime.now().date() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=date)
        return queryset
