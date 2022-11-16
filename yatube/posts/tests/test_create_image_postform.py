import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        self.form_data = {
            'text': 'Тестовый новый пост',
            'group': self.group.id,
            'image': uploaded,
        }

    def test_create_post(self):
        """Проверяет, что при отправке поста с картинкой
        через форму PostForm создаётся запись в базе данных."""

        self.response = self.authorized_client.post(
            reverse('posts:post_create'), data=self.form_data, follow=True
        )
        # Проверяем кол-во постов
        self.assertEqual(Post.objects.count(), 2)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            self.response, reverse('posts:profile', args=[self.user])
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(text=self.form_data['text']).exists()
        )
        # Проверяем отправку поста с картинкой через форму PostForm.
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый новый пост',
                group=self.group,
                image='posts/small.gif',
            ).exists()
        )
        last_post = Post.objects.first()
        self.assertEqual(last_post.id, 2)
        self.assertEqual(last_post.text, 'Тестовый новый пост')
        self.assertEqual(last_post.group, self.post.group)
        self.assertEqual(last_post.author, self.post.author)
        self.assertEqual(last_post.image.size, self.form_data['image'].size)
        # Шаблон post_detail содержит один пост отфильтрованный по id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 2})
        )
        self.assertEqual(response.context.get('post'), last_post)

    def test_edit_post(self):
        """Проверяет, что при редактировании поста с картинкой
        через форму PostForm создаётся запись в базе данных."""
        # Проверяем, сработал ли редирект
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=self.form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        # Проверяем, что создалась запись с заданным текстом assertEquals()
        self.assertTrue(
            Post.objects.filter(text=self.form_data['text']).exists()
        )
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
        self.assertEqual(last_post.image.size, self.form_data['image'].size)
