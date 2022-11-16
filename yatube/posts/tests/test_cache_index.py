from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Post

User = get_user_model()


class CachePageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def test_index_cache(self):
        """Проверка работы cache, три запроса response.content."""
        Post.objects.create(
            text='Новый пост',
            author=self.user,
        )
        first_response = self.authorized_client.get(reverse('posts:index'))
        content_first = first_response.content
        post = Post.objects.get(id=1)
        post.delete()
        second_response = self.authorized_client.get(reverse('posts:index'))
        content_second = second_response.content
        self.assertEqual(content_first, content_second)
        cache.clear()
        third_response = self.authorized_client.get(reverse('posts:index'))
        content_third = third_response.content
        self.assertNotEqual(content_second, content_third)
