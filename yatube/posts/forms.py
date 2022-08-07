from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:

        model = Post
        help_text = 'Текст сообщения и группа'
        fields = ('group', 'text')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        help_text = 'Текст сообщения и группа'
        fields = ('text', )
