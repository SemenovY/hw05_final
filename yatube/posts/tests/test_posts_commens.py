from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class PostCommentTests(TestCase):
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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        """Проверяем что при отправке валидной формы
        со страницы создания комментария reverse('posts:add_comment')
        создаётся новая запись в базе данных."""
        comment_count = Comment.objects.count()
        comment_data = {
            'text': 'Новый комментарий',
        }
        # Проверяем кол-во постов
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        post = Post.objects.first()
        for comment in post.comments.all():
            self.assertEqual(comment.text, comment_data['text'])
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Comment.objects.filter(text=comment_data['text']).exists()
        )
        # Проверяем, что происходит изменение поста с post_id в базе данных
        last_post = Post.objects.first()
        self.assertEqual(last_post.id, self.post.id)
        self.assertEqual(last_post.text, self.post.text)
        self.assertEqual(last_post.group, self.post.group)
        self.assertEqual(last_post.author, self.post.author)

    def test_post_comment_url_exists_at_desired_location_anonymous(self):
        """Страница /comment/ доступна только авторизованному пользователю."""
        response = self.guest_client.get(f'/posts/{self.post.id}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
