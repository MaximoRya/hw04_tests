"""Создание моделей Group и Posts для админ-зоны сайта."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для работы с группами в базе данных."""
    title = models.CharField(max_length=200)
    slug = models.SlugField('Код в url', unique=True)
    description = models.TextField('Описание', max_length=500)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        """Метод, который возвращает строковое представление объекта."""
        return self.title


class Post(models.Model):
    """Модель для работы с постами в базе данных."""

    text = models.TextField(
        'Текст',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Автор',
        verbose_name='Автор',
        help_text='ID автора сообщения'
    )

    group = models.ForeignKey(
        Group, blank=True,
        null=True, on_delete=models.SET_NULL,
        related_name='posts',
    )

    class Meta:
        verbose_name = 'Сообщение',
        verbose_name_plural = 'Сообщения',
        ordering = ('-pub_date'),

    def __str__(self):
        """Метод, который возвращает строковое представление объекта."""
        return self.text[:15]
