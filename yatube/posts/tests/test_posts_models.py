from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_text(self):
        """Проверяем, правильно ли отображается значение поля __str__
        для класса Post — первые пятнадцать символов поста."""
        max_length_text = Post._meta.get_field('text').max_length
        length_text = len(self.post.text)
        self.assertNotEqual(max_length_text, length_text)

    def test_verbose_name_post(self):
        """Проверяем verbose_name модели Post."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """Проверяем help_text модели Post."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_slug(self):
        """Проверяем, правильно ли отображается значение поля __str__
        для класса Group — название группы."""
        expected_object_slug = self.group.slug
        self.assertEqual(expected_object_slug, str(self.group.slug))

    def test_verbose_name_group(self):
        """Проверяем verbose_name модели Group."""
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEquals(
                    Group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_group(self):
        """Проверяем help_text модели Group."""
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Укажите адрес для страницы группы',
            'description': 'Укажите описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).help_text, expected_value
                )
