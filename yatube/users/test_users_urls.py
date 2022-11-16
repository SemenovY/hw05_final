from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutURLTests(TestCase):
    """Проверяем что страницы доступны по ожидаемому адресу."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(AboutURLTests.user)

    def test_guest_url_exists_at_desired_location(self):
        """Проверка доступности URL адресов."""
        urls = [
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/signup/',
            '/auth/logout/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        для авторизованного и не авторизованного пользователя."""
        password_reset_confirm = 'users/password_reset_confirm.html'
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/about/tech/': 'about/tech.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/': password_reset_confirm,
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_authorized_client_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        для авторизованного пользователя."""
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_password_change_url_exists_at_desired_location(self):
        """Страница /password_change/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url_exists_at_desired_location(self):
        """Страница /password_change_done/
        доступна авторизованному пользователю."""
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
