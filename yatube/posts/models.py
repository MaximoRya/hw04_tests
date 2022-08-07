"""Создание моделей Group и Posts для админ-зоны сайта."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для работы с группами в базе данных."""
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField('Код группы в url', unique=True)
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
        related_name='posts',
        verbose_name='Автор',
        help_text='ID автора сообщения'
    )

    group = models.ForeignKey(
        Group, blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )

    # Поле для картинки (необязательное)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        verbose_name = 'Сообщение',
        verbose_name_plural = 'Сообщения',
        ordering = ('-pub_date'),

    def __str__(self):
        """Метод, который возвращает строковое представление объекта."""
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментарии'
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария',
                               )
    post = models.ForeignKey(
                            Post,
                            on_delete=models.CASCADE,
                            related_name='comments',
                            verbose_name='Я пока не понял',
                        )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
