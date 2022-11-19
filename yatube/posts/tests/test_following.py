from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post

User = get_user_model()


class PostFollowTests(TestCase):
    """Проверяют работу подписки на автора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1')
        cls.auth = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.post = Post.objects.create(
            author=self.auth,
            text='Тестовый пост автора',
        )

    def tearDown(self):
        cache.clear()

    def test_follow(self):
        """Авторизованный пользователь
        может подписываться на других пользователей."""
        follow_count = Follow.objects.count()
        if self.post.author != self.user1:
            self.authorized_client1.get(f'/profile/{self.auth}/follow/')
            response = self.authorized_client1.get('/follow/')
            self.assertEqual(response.context.get('post'), self.post)
            # Проверяем число постов
            self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        """Авторизованный пользователь
        может удалять подписки."""
        follow_count = Follow.objects.count()
        form_data = {
            'text': self.post.text,
        }
        if self.post.author != self.user1:
            Follow.objects.get_or_create(user=self.user1, author=self.auth)
        response = self.authorized_client1.post(
            reverse('posts:profile_follow', kwargs={'username': 'auth'}),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'auth'})
        )
        # Отписываемся
        self.authorized_client1.get(f'/profile/{self.auth}/unfollow/')
        # Сравниваем
        response = self.authorized_client1.get('/follow/')
        self.assertNotEqual(response.context.get('post'), self.post)
        # Проверяем число постов
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_followed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.."""
        follow_count = Follow.objects.count()
        # Создаем пользователя
        user2 = User.objects.create_user(username='user2')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(user2)
        # Проверяем что в follow_index для него ничего не возвращается
        response = self.authorized_client2.get('/follow/')
        self.assertNotEqual(response.context.get('post'), self.post)
        # Проверяем число постов
        self.assertEqual(Follow.objects.count(), follow_count)
