from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
