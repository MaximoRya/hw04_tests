from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:

        model = Post
        help_text = 'Введите текст сообщения и выберете группу'
        fields = ['text', 'group']
