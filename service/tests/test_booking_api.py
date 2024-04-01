from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from service.models import Room, Booking


class BookingApiTestCase(APITestCase):
    def setUp(self):
        url_login = reverse('auth:login')
        url_register = reverse('auth:register')

        self.client.post(url_register, data={
            'username': 'user_1',
            'password1': 'userpassword123',
            'password2': 'userpassword123'
        })
        self.user_1_id = User.objects.last().id
        self.client.post(url_register, data={
            'username': 'user_2',
            'password1': 'userpassword123',
            'password2': 'userpassword123'
        })
        self.user_2_id = User.objects.last().id
        response = self.client.post(url_login, data={
            'username': 'user_1',
            'password': 'userpassword123'
        })
        self.token_user_1 = response.data['key']
        response = self.client.post(url_login, data={
            'username': 'user_2',
            'password': 'userpassword123'
        })
        self.token_user_2 = response.data['key']

        self.superuser = User.objects.create_superuser(username='superuser',
                                                       password='password')
        response = self.client.post(url_login, data={
            'username': 'superuser',
            'password': 'password'
        })
        self.token_superuser = response.data['key']

        self.room_1 = Room.objects.create(number='111',
                                          cost_per_day=100, beds=1)
        self.room_2 = Room.objects.create(number='222',
                                          cost_per_day=200, beds=2)

    def test_create_booking(self):
        url = reverse('booking:booking-list')
        data_1 = {
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }
        data_2 = {
            'room': self.room_1.id,
            'start_time': '2024-06-01T09:10:01Z',
            'end_time': '2024-06-10T09:10:01Z'
        }
        data_3 = {
            'room': self.room_1.id,
            'start_time': '2024-07-29T09:10:01Z',
            'end_time': '2024-08-29T09:10:01Z'
        }

        response = self.client.post(url, data=data_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data=data_2, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data=data_3, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_booking_list(self):
        url = reverse('booking:booking-list')
        data_1 = {
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }
        data_2 = {
            'room': self.room_2.id,
            'start_time': '2024-06-01T09:10:01Z',
            'end_time': '2024-06-10T09:10:01Z'
        }

        self.client.post(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        booking_1_id = Booking.objects.last().id

        self.client.post(url, data=data_2, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        booking_2_id = Booking.objects.last().id

        expected_data_1 = [
            {
                'id': booking_1_id,
                'client': self.user_1_id,
                'room': self.room_1.id,
                'start_time': '2024-05-29T09:10:01Z',
                'end_time': '2024-06-29T09:10:01Z'
            }
        ]
        expected_data_2 = [
            {
                'id': booking_2_id,
                'client': self.user_2_id,
                'room': self.room_2.id,
                'start_time': '2024-06-01T09:10:01Z',
                'end_time': '2024-06-10T09:10:01Z'
            }
        ]

        expected_data_3 = [
            {
                'id': booking_1_id,
                'client': self.user_1_id,
                'room': self.room_1.id,
                'start_time': '2024-05-29T09:10:01Z',
                'end_time': '2024-06-29T09:10:01Z'
            },
            {
                'id': booking_2_id,
                'client': self.user_2_id,
                'room': self.room_2.id,
                'start_time': '2024-06-01T09:10:01Z',
                'end_time': '2024-06-10T09:10:01Z'
            }
        ]

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data_1, response.data)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data_2, response.data)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data_3, response.data)

    def test_booking_detail(self):
        url = reverse('booking:booking-list')
        data_1 = {
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }
        data_2 = {
            'room': self.room_2.id,
            'start_time': '2024-06-01T09:10:01Z',
            'end_time': '2024-06-10T09:10:01Z'
        }

        self.client.post(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        booking_1_id = Booking.objects.last().id

        self.client.post(url, data=data_2, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        booking_2_id = Booking.objects.last().id

        expected_data_1 = {
            'id': booking_1_id,
            'client': self.user_1_id,
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }

        expected_data_2 = {
            'id': booking_2_id,
            'client': self.user_2_id,
            'room': self.room_2.id,
            'start_time': '2024-06-01T09:10:01Z',
            'end_time': '2024-06-10T09:10:01Z'
        }

        url_user_1 = reverse('booking:booking-detail', args=(booking_1_id,))
        url_user_2 = reverse('booking:booking-detail', args=(booking_2_id,))

        response = self.client.get(url_user_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data_1, response.data)

        response = self.client.get(url_user_2, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data_2, response.data)

        response = self.client.get(url_user_2, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data_2, response.data)

    def test_update_booking(self):
        url = reverse('booking:booking-list')

        data_1 = {
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }
        data_2 = {
            'client': self.user_1_id,
            'room': self.room_1.id,
            'start_time': '2024-07-29T09:10:01Z',
            'end_time': '2024-08-29T09:10:01Z'
        }

        self.client.post(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        booking_1_id = Booking.objects.last().id

        url_user_1 = reverse('booking:booking-detail', args=(booking_1_id,))

        response = self.client.put(url_user_1, data=data_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url_user_1, data=data_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url_user_1, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(url_user_1, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(url_user_1, data=data_2, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': booking_1_id,
            'client': self.user_1_id,
            'room': self.room_1.id,
            'start_time': '2024-07-29T09:10:01Z',
            'end_time': '2024-08-29T09:10:01Z'
        })

        response = self.client.patch(url_user_1, data=data_1, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': booking_1_id,
            'client': self.user_1_id,
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        })

    def test_delete_booking(self):
        url = reverse('booking:booking-list')

        data_1 = {
            'room': self.room_1.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }

        data_2 = {
            'room': self.room_2.id,
            'start_time': '2024-05-29T09:10:01Z',
            'end_time': '2024-06-29T09:10:01Z'
        }

        self.client.post(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        booking_1_id = Booking.objects.last().id

        self.client.post(url, data=data_2, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        booking_2_id = Booking.objects.last().id

        url_user_1 = reverse('booking:booking-detail', args=(booking_1_id,))
        url_user_2 = reverse('booking:booking-detail', args=(booking_2_id,))

        response = self.client.delete(url_user_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url_user_1, headers={
            'Authorization': f'Token {self.token_user_2}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url_user_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Booking.objects.all().count(), 1)

        response = self.client.delete(url_user_2, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Booking.objects.all().count(), 0)


