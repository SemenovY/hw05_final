from core.models import CreatedModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Введите название группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес',
        help_text='Укажите адрес для страницы группы',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Укажите описание группы',
    )

    class Meta:
        verbose_name = 'группу'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка к посту',
        help_text='Добавьте каринку к посту',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[: settings.LEN_TEXT_STR]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарии',
        help_text='Комментарий для поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    models.UniqueConstraint(fields=['user', 'author'], name='unique_follow')

    class Meta:
        verbose_name = 'подписчика'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.user
