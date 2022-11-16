from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Cats',
            description='Тестовое описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяем что при отправке валидной формы
        со страницы создания поста reverse('posts:post_create')
        создаётся новая запись в базе данных."""

        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }
        # Проверяем, сработал ли редирект
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user])
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())

    def test_edit_post(self):
        """Проверяем что при отправке валидной формы
        со страницы редактирования поста
        reverse('posts:post_edit', args=('post_id',))
        происходит изменение поста с post_id в базе данных."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.id,
        }
        # Проверяем, сработал ли редирект
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        # Проверяем, что создалась запись с заданным текстом assertEquals()
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        # Проверяем, что происходит изменение поста в базе данных
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)
        # Проверяем, что происходит изменение поста с post_id в базе данных
        last_post = Post.objects.first()
        self.assertEqual(last_post.id, self.post.id)
        self.assertNotEqual(last_post.text, self.post.text)
        self.assertEqual(last_post.group, self.post.group)
        self.assertEqual(last_post.author, self.post.author)
