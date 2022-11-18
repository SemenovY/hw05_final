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
        cls.user2 = User.objects.create_user(username='user2')
        cls.auth = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        self.post = Post.objects.create(
            author=self.auth,
            text='Тестовый пост автора',
        )

    def tearDown(self):
        cache.clear()

    # def test_following(self):
    #     """Авторизованный пользователь
    #     может подписываться на других пользователей и удалять их."""
    #     follow_count = Follow.objects.count()
    #     if self.post.author != self.user1:
    #         Follow.objects.get_or_create(user=self.user1, author=self.auth)
    #     response = self.authorized_client1.post(
    #         reverse('posts:profile_follow', kwargs={'username': 'auth'}),
    #         data=self.post.text,
    #         follow=True,
    #     )

    #     # Проверяем число постов
    #     self.assertEqual(Follow.objects.count(), follow_count + 1)

    #     # Отписка
    #     response = self.authorized_client1.post(
    #         reverse('posts:profile_unfollow', kwargs={'username': 'auth'}),
    #     )

    #     # Проверяем число постов
    #     self.assertEqual(Follow.objects.count(), follow_count)

    def test_following2(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.."""
        follow_count = Follow.objects.count()
        form_data = {
            'text': self.post.text,
        }
        if self.post.author != self.user1 and self.user2:
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
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        # profile содержит список постов отфильтрованных по пользователю
        posts_list1 = Post.objects.filter(
            author__following__user=self.user1
        ).all()
        posts_list2 = Post.objects.filter(
            author__following__user=self.user2
        ).all()
        # Сравниваем.
        self.assertNotEqual(posts_list1, posts_list2)
