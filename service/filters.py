from datetime import datetime

from django.db.models import Q
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from service.models import Room


class RoomFilter(FilterSet):
    """
    Filter class for RoomViewSet.
    """
    available_rooms = CharFilter(method='filter_available_rooms')
    beds = NumberFilter()
    cost_per_day = NumberFilter()

    def filter_available_rooms(self, queryset, name, value):
        start_time, end_time = [datetime.strptime(val, '%y-%m-%d_%H:%M:%S').astimezone()
                                for val in value.split(',')]
        return queryset.exclude(Q(bookings__start_time__range=(start_time, end_time)) |
                                Q(bookings__end_time__range=(start_time, end_time)) |
                                Q(bookings__start_time__lte=start_time) & Q(bookings__end_time__gte=end_time))

    class Meta:
        model = Room
        fields = ['beds', 'cost_per_day']
