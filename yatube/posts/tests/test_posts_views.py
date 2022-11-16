from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    """Проверяем что страницы доступны по ожидаемому адресу."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Cats',
            description='Тестовое описание',
        )
        cls.group_test = Group.objects.create(
            title='Тестовая группа 2',
            slug='Diary',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author},
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index содержит список постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author.username, 'auth')
        self.assertEqual(first_object.group.slug, self.group.slug)
        self.assertEqual(response.context.get('post'), self.post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list содержит список постов отфильтрованных
        по группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        group = get_object_or_404(Group, slug=self.group.slug)
        self.assertEqual(response.context.get('group'), group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile содержит список постов отфильтрованных
        по пользователю."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username, 'auth')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail содержит один пост отфильтрованный по id."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_edit_page_show_correct_context(self):
        """Проверяем что шаблон create_post содержит форму редактирования поста
        отфильтрованного по id, что она является инстансом и is_edit."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)
        self.assertTrue(response.context.get('is_edit'))
        post_form = PostPagesTests()
        self.assertIsInstance(post_form, PostPagesTests, msg=None)
        self.assertIn('form', response.context)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post содержит форму создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_group_page_show_correct_context(self):
        """Проверяем, если при создании поста указать группу,
        то этот пост появляется на главной странице сайта,
        на странице выбранной группы, в профайле пользователя."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author.username, 'auth')
        self.assertEqual(first_object.group.slug, self.group.slug)
        # на странице выбранной группы
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author.username, 'auth')
        self.assertEqual(first_object.group.slug, self.group.slug)
        # в профайле пользователя
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author.username, 'auth')
        self.assertEqual(first_object.group.slug, self.group.slug)

    def test_post_is_not_in_another_group(self):
        """Созданный пост не попал в группу, для которой
        не был предназначен."""
        Post.objects.create(
            author=self.user, text='Тестовый пост ', group=self.group_test
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_test.slug})
        )
        post_new = response.context["page_obj"][0]
        self.assertNotEqual(post_new, self.post)
