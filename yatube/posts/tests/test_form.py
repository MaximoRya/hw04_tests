# posts/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #  Создаём группу
        cls.group = Group.objects.create(
            title='group_test',
            slug='slug_test',
            description='descr_test',

        )
        cls.group_1 = Group.objects.create(
            title='group_1',
            slug='slug_1',
            description='descr_test',

        )
        # Создадим запись в БД для проверки доступности адресов страниц
        cls.user_author = User.objects.create_user(username='author_test')
        cls.form = PostForm()
        # Создадим запись в БД для проверки доступности адресов страниц
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group_1
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user_author)

        self.post = Post.objects.create(
            author=PostPagesTests.user_author,
            group=PostPagesTests.group,
            text='Тестовый без группы пост',
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        group = self.post.group.slug
        post_author = self.post.author
        postik_id = self.post.pk
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': f'{post_author}'}
            ): 'posts/profile.html',
            reverse(
                'posts:group_list', kwargs={'slug': f'{group}'}
            ): 'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{postik_id}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{postik_id}'}
            ): 'posts/create_post.html',
        }
        # Проверяем HTML-шаблон при обращении к name
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post(self):
        """Валидная форма создает Пост в БД."""
        # Подсчитаем количество записей в Task
        post_count = Post.objects.count()
        form_data = {
            'text': 'texto_testo',
            'group': f'{self.post.group.id}',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        post_author = self.post.author
        self.assertRedirects(response, (reverse(
            'posts:profile', kwargs={'username': f'{post_author}'}
        )))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась новая запись
        self.assertTrue(
            Post.objects.filter(
                text='texto_testo',
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует Пост в БД."""

        form_data = {
            'text': 'texto_testo',
            'group': f'{self.post.group.id}',
        }
        # Отправляем POST-запрос
        postik_id = self.post.id
        response = self.authorized_client.post((
            reverse('posts:post_edit', kwargs={'post_id': f'{postik_id}'})),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, (
            reverse('posts:post_detail', kwargs={'post_id': f'{postik_id}'})
        ))
        # Проверяем, что создалась новая запись
        self.assertTrue(
            Post.objects.filter(
                text='texto_testo',
                group=self.group.id

            ).exists()
        )
