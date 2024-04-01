from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationTestCase(APITestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password_1 = 'testuserpassword123'
        self.password_2 = 'testuserpassword123'
        self.password = 'testuserpassword123'

    def test_registration(self):
        url = reverse('auth:register')

        response = self.client.post(url, data={
            'username': self.username,
            'password1': self.password_1,
            'password2': self.password_2
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user = User.objects.last()
        self.assertEqual(self.username, user.username)

        response = self.client.post(url, data={
            'username': self.username,
            'password1': self.password_1,
            'password2': self.password_2
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data={
            'password1': self.password_1,
            'password2': self.password_2
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data={
            'username': self.username,
            'password2': self.password_2
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data={
            'username': self.username,
            'password1': self.password_1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_and_get_user_details(self):
        url_login = reverse('auth:login')
        url_user_details = reverse('auth:user-details')
        url_register = reverse('auth:register')

        response = self.client.post(url_login, data={
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(url_user_details)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.post(url_register, data={
            'username': self.username,
            'password1': self.password_1,
            'password2': self.password_2
        })

        response = self.client.post(url_login, data={
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = response.data['key']

        response = self.client.get(url_user_details, headers={
            'Authorization': f'Token {token}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

    def test_update_user(self):
        url_user_details = reverse('auth:user-details')
        url_register = reverse('auth:register')
        url_login = reverse('auth:login')

        response = self.client.put(url_user_details, data={
            'username': 'newusername',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url_user_details, data={
            'username': 'newusername',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.post(url_register, data={
            'username': self.username,
            'password1': self.password_1,
            'password2': self.password_2
        })

        response = self.client.post(url_login, data={
            'username': self.username,
            'password': self.password,
        })

        token = response.data['key']

        response = self.client.put(url_user_details, data={
            'username': 'newusername',
        }, headers={
            'Authorization': f'Token {token}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'newusername')

        self.assertEqual(User.objects.last().username, 'newusername')

        response = self.client.patch(url_user_details, data={
            'username': self.username,
        }, headers={
            'Authorization': f'Token {token}'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

        self.assertEqual(User.objects.last().username, self.username)

    def test_logout(self):
        url_register = reverse('auth:register')
        url_login = reverse('auth:login')
        url_logout = reverse('auth:logout')

        response = self.client.patch(url_logout, data={
            'username': self.username,
        }, headers={
            'Authorization': f'Token testtoken'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.post(url_register, data={
            'username': self.username,
            'password1': self.password_1,
            'password2': self.password_2
        })

        response = self.client.post(url_login, data={
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = response.data['key']

        response = self.client.post(url_logout, headers={
            'Authorization': f'Token {token}'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
