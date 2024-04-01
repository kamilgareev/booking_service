from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from service.models import Room, Booking


class RoomApiTestCase(APITestCase):
    def setUp(self):
        url_login = reverse('auth:login')
        url_register = reverse('auth:register')

        self.client.post(url_register, data={
            'username': 'user_1',
            'password1': 'userpassword123',
            'password2': 'userpassword123'
        })
        self.client.post(url_register, data={
            'username': 'user_2',
            'password1': 'userpassword123',
            'password2': 'userpassword123'
        })
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

    def test_room_list(self):
        url = reverse('booking:room-list')

        expected_data = [
            {
                'id': self.room_1.id,
                'number': '111',
                'cost_per_day': '100.00',
                'beds': 1
            },
            {
                'id': self.room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            }
        ]

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_room_detail(self):
        url = reverse('booking:room-detail', args=(self.room_1.id,))

        expected_data = {
            'id': self.room_1.id,
            'number': '111',
            'cost_per_day': '100.00',
            'beds': 1
        }

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

        response = self.client.get(url, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_create_room(self):
        url = reverse('booking:room-list')
        data = {
            'number': '333',
            'cost_per_day': '300.00',
            'beds': 3
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url, data=data, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(url, data=data, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Room.objects.all().count(), 3)

    def test_update_room(self):
        url = reverse('booking:room-detail', args=(self.room_1.id,))

        data_1 = {
            'number': '333',
            'cost_per_day': '300.00',
            'beds': 3
        }

        data_2 = {
            'number': '111',
            'cost_per_day': '100.00',
            'beds': 1
        }

        response = self.client.put(url, data=data_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data=data_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data=data_1, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(url, data=data_1, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.room_1.id,
            'number': '333',
            'cost_per_day': '300.00',
            'beds': 3
        })
        response = self.client.patch(url, data=data_2, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.room_1.id,
            'number': '111',
            'cost_per_day': '100.00',
            'beds': 1
        })

    def test_delete_room(self):
        url = reverse('booking:room-detail', args=(self.room_1.id,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url, headers={
            'Authorization': f'Token {self.token_user_1}'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url, headers={
            'Authorization': f'Token {self.token_superuser}'
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Room.objects.all().count(), 1)

    def test_ordering(self):
        url = reverse('booking:room-list')

        room_3 = Room.objects.create(number='333',
                                     cost_per_day=700, beds=5)
        room_4 = Room.objects.create(number='444',
                                     cost_per_day=50, beds=1)

        expected_data_cost_per_day = [
            {
                'id': room_4.id,
                'number': '444',
                'cost_per_day': '50.00',
                'beds': 1
            },
            {
                'id': self.room_1.id,
                'number': '111',
                'cost_per_day': '100.00',
                'beds': 1
            },
            {
                'id': self.room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            },
            {
                'id': room_3.id,
                'number': '333',
                'cost_per_day': '700.00',
                'beds': 5
            },
        ]

        expected_data_beds = [
            {
                'id': self.room_1.id,
                'number': '111',
                'cost_per_day': '100.00',
                'beds': 1
            },
            {
                'id': room_4.id,
                'number': '444',
                'cost_per_day': '50.00',
                'beds': 1
            },
            {
                'id': self.room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            },
            {
                'id': room_3.id,
                'number': '333',
                'cost_per_day': '700.00',
                'beds': 5
            },
        ]
        response = self.client.get(url, data={'ordering': 'cost_per_day'})
        self.assertEqual(expected_data_cost_per_day, response.data)

        response = self.client.get(url, data={'ordering': 'beds'})
        self.assertEqual(expected_data_beds, response.data)

    def test_filter(self):
        url = reverse('booking:room-list')
        room_3 = Room.objects.create(number='333',
                                     cost_per_day=300, beds=1)

        expected_data_cost_per_day = [
            {
                'id': self.room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            }
        ]

        response = self.client.get(url, data={'cost_per_day': '200.00'})
        self.assertEqual(expected_data_cost_per_day, response.data)

        expected_data_beds = [
            {
                'id': self.room_1.id,
                'number': '111',
                'cost_per_day': '100.00',
                'beds': 1
            },
            {
                'id': room_3.id,
                'number': '333',
                'cost_per_day': '300.00',
                'beds': 1
            },
        ]
        response = self.client.get(url, data={'beds': '1'})
        self.assertEqual(expected_data_beds, response.data)

    def test_available_rooms(self):
        url = reverse('booking:room-list')
        user = User.objects.create(username='user', password='userpassword123')
        expected_data_1 = [
            {
                'id': self.room_1.id,
                'number': '111',
                'cost_per_day': '100.00',
                'beds': 1
            },
            {
                'id': self.room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            },
        ]
        expected_data_2 = [
            {
                'id': self.room_2.id,
                'number': '222',
                'cost_per_day': '200.00',
                'beds': 2
            },
        ]
        response = self.client.get(url, data={'start_time': '24-04-21_09:10:01',
                                              'end_time': '24-05-21_09:10:01'})
        self.assertEqual(expected_data_1, response.data)

        Booking.objects.create(room=self.room_1, client=user,
                               start_time='2024-04-22T09:10:01Z',
                               end_time='2024-04-25T09:10:01Z')

        response = self.client.get(url, data={'start_time': '24-04-21_09:10:01',
                                              'end_time': '24-05-21_09:10:01'})
        self.assertEqual(expected_data_2, response.data)

        Booking.objects.create(room=self.room_2, client=user,
                               start_time='2024-05-20T09:10:01Z',
                               end_time='2024-06-20T09:10:01Z')

        response = self.client.get(url, data={'start_time': '24-04-21_09:10:01',
                                              'end_time': '24-05-21_09:10:01'})
        self.assertEqual([], response.data)


