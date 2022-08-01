"""Создаём интерфейс админ зоны сайта."""
from django.contrib import admin

from posts.models import Group, Post
from yatube.settings import EMPTY_VALUE_DISPLAY


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Формируем панель админа."""

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(Group)
