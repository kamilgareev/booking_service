from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from service.filters import RoomFilter
from service.models import Room, Booking
from service.permissions import IsAdminOrReadOnly, IsAdminOrRoomClient
from service.serializers import RoomSerializer, BookingSerializer


@extend_schema(tags=['Комнаты, модель Room'])
@extend_schema_view(
    list=extend_schema(
        summary='Получение списка комнат',
        description="""Получение список комнат.Возможно указание параметров 'start_time' и 
        'end_time' в url для получения списка свободных комнат в указанный временной период.
        Пример такого url: '.../booking/room/?start_time=24-03-29_09:10:01&end_time=24-05-29_09:11:11'.
        Доступно всем пользователем, в том числе и неавторизованным."""
    ),
    retrieve=extend_schema(
        summary='Получение информации о конкретной комнате',
        description='Доступно всем пользователем, в том числе и неавторизованным.'
    ),
    update=extend_schema(
        summary='Изменение параметров комнаты',
        description='Доступно только суперюзеру.'
    ),
    partial_update=extend_schema(
        summary='Частичное зменение параметров комнаты',
        description='Доступно только суперюзеру.'
    ),
    create=extend_schema(
        summary='Создание новой комнаты',
        description='Доступно только суперюзеру.'
    ),
    destroy=extend_schema(
        summary='Удаление комнаты',
        description='Доступно только суперюзеру.'
    ),
)
class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RoomFilter
    ordering_fields = ['cost_per_day', 'beds']


@extend_schema(tags=['Бронирования, модель Booking'])
@extend_schema_view(
    list=extend_schema(
        summary='Получение списка бронирований',
        description='Доступно только суперюзеру.'
    ),
    retrieve=extend_schema(
        summary='Получение информации о конкретном бронировании',
        description='Доступно суперюзеру и владельцу бронирования.'
    ),
    update=extend_schema(
        summary='Изменение параметров бронирования',
        description='Доступно только суперюзеру.'
    ),
    partial_update=extend_schema(
        summary='Частичное зменение параметров бронирования',
        description='Доступно только суперюзеру.'
    ),
    create=extend_schema(
        summary='Создание бронирования',
        description='Доступно всем авторизованным пользователям. Время бронирования '
                    'проходит проверку на предмет пересечения с другими бронированиями указанной комнаты.'
    ),
    destroy=extend_schema(
        summary='Удаление бронирования',
        description='Доступно владельцу бронирования и суперюзеру.'
    ),
)
class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrRoomClient]
    serializer_class = BookingSerializer

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.filter_queryset(self.get_queryset()).filter(client=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
