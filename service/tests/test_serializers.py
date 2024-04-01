from django.contrib.auth.models import User
from django.test import TestCase

from service.models import Room, Booking
from service.serializers import RoomSerializer, BookingSerializer


class RoomSerializerTestCase(TestCase):
    def test_room_serializer(self):
        room_1 = Room.objects.create(number='111',
                                     cost_per_day=100, beds=1)
        room_2 = Room.objects.create(number='222',
                                     cost_per_day=200, beds=2)
        rooms = Room.objects.all()
        serializer_data = RoomSerializer(rooms, many=True).data

        expected_data = [
            {
                'id': room_1.id,
                'number': '111',
                'cost_per_day': '100.00',
                'beds': 1
            },
            {
                'id': room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            }
        ]

        self.assertEqual(expected_data, serializer_data)


class BookingSerializerTestCase(TestCase):
    def test_booking_serializer(self):
        user_1 = User.objects.create(username='user_1',
                                     password='password')
        user_2 = User.objects.create(username='user_2',
                                     password='password')
        room_1 = Room.objects.create(number='111',
                                     cost_per_day=100, beds=1)
        room_2 = Room.objects.create(number='222',
                                     cost_per_day=200, beds=2)
        booking_1 = Booking.objects.create(room=room_1, client=user_1,
                                           start_time='2024-03-29 09:10:01+00:00',
                                           end_time='2024-05-29 09:11:11+00:00')
        booking_2 = Booking.objects.create(room=room_2, client=user_2,
                                           start_time='2024-07-29 09:10:01+00:00',
                                           end_time='2024-09-29 09:11:11+00:00')

        bookings = Booking.objects.all()
        serializer_data = BookingSerializer(bookings, many=True).data
        expected_data = [
            {
                'id': booking_1.id,
                'room': room_1.id,
                'client': user_1.id,
                'start_time': '2024-03-29T09:10:01Z',
                'end_time': '2024-05-29T09:11:11Z'
            },
            {
                'id': booking_2.id,
                'room': room_2.id,
                'client': user_2.id,
                'start_time': '2024-07-29T09:10:01Z',
                'end_time': '2024-09-29T09:11:11Z'
            },
        ]

        self.assertEqual(expected_data, serializer_data)
