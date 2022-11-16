from random import randrange

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
PAGE_N = settings.NUMBER_OF_PAGES * 2 - randrange(1, settings.NUMBER_OF_PAGES)


class PostPaginatorsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Cats',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовые посты номер {n}',
                    author=cls.user,
                    group=cls.group,
                )
                for n in range(PAGE_N)
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.page_two = PAGE_N - settings.NUMBER_OF_PAGES
        self.templates_page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]

    def test_first_page_index_contains_ten_records(self):
        """Тестируем paginator на главной странице, group_list, profile."""

        for reverse_name in self.templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), settings.NUMBER_OF_PAGES
                )

    def test_second_page_index_contains_three_records(self):
        """Тестируем paginator на 2 странице index, group_list, profile."""

        for reverse_name in self.templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), self.page_two
                )
