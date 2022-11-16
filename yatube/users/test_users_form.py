from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class UserFormTests(TestCase):
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
        self.authorized_client = Client()
        self.authorized_client.force_login(UserFormTests.user)

    def test_create_user(self):
        """Проверяем что при заполнении формы
        reverse('users:signup') создаётся новый пользователь."""

        form_data = {
            'text': 'Тестовый пост',
            'group': UserFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('users:signup'), data=form_data, follow=True
        )
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(User.objects.filter(username='auth').exists())
        self.assertEqual(response.context.get('user'), self.user)
        last_user = User.objects.first()
        self.assertEqual(last_user.id, self.user.id)
