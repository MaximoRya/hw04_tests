from django import forms
from .models import Post

class PostForm(forms.ModelForm):
        class Meta:
                model = Post
                fields = ('group','text')


# class PostForm(forms.Form):
#         group = forms.ModelChoiceField(required=False, queryset=Group.objects.all())
#         text = forms.CharField(widget=forms.Textarea)