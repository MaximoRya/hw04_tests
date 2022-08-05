# posts/tests/test_views.py
from distutils.command import upload
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

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
        cls.user = User.objects.create_user(username='author_test')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        # Создадим запись в БД для проверки доступности адресов страниц
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group_1
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.form = PostForm()
        cls.form_data = {
            'text': 'New',
            'group': cls.group.id,
            'image': uploaded
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostPagesTests.post.author)

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
        # Проверяем, что вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        context_index = response.context.get('posts')[1].text
        # Проверяем, что в посте указана группа
        self.assertIsNotNone(response.context.get('posts')[0].group)
        expected = self.post.text
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_index, expected)

    def test_group_list_page_show_correct_context(self):
        """Шаблон gruop_list сформирован с правильным контекстом."""
        post_group = self.post.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{post_group}'})
        )
        context_gruop_list_group = response.context.get('page_obj')[0].group
        context_gruop_list_text = response.context.get('page_obj')[0].text
        expected_group = self.post.group
        expected_text = self.post.text
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_gruop_list_group, expected_group)
        self.assertEqual(context_gruop_list_text, expected_text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post_author = self.post.author
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': f'{post_author}'})
        )
        context_profile_author = response.context.get('page_obj')[0].author
        context_profile_text = response.context.get('page_obj')[0].text
        expected_author = self.post.author
        expected_text = self.post.text
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_author, expected_author)
        self.assertEqual(context_profile_text, expected_text)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_id = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post_id}'})
        )
        context_post_id = response.context.get('post').id
        expected = self.post.id
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_post_id, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_group_list_page_show_correct_context(self):
        """Пост не попал не в свою группу не отображается в другой группе"""
        post_group = 'slug-check'
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{post_group}'})
        )
        context_gruop_list_text = response.context.get('page_obj')
        expected = None
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_gruop_list_text, expected)

    def test_index_image_context(self):
        """Шаблон index сформирован с картинкой в контексте."""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        context_profile_image = response.context.get('page_obj')[0].image
        expected_image = self.post.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_image, expected_image)

    def test_profile_image_context(self):
        """Шаблон profile сформирован с картинкой в контексте."""
        post_author = self.post.author
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': f'{post_author}'})
        )
        context_profile_image = response.context.get('page_obj')[0].image
        expected_image = self.post.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_image, expected_image)

    def test_post_detail_image_context(self):
        """Шаблон post_detail сформирован с картинкой в контексте."""
        post_id = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post_id}'})
        )
        context_profile_image = response.context.get('post').image
        expected_image = self.post.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_image, expected_image)

    def test_group_image_context(self):
        """Шаблон group_list сформирован с картинкой в контексте."""
        post_group = self.post.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{post_group}'})
        )
        context_group_list_image = response.context.get('page_obj')[0].image
        expected_image = self.post.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_group_list_image, expected_image)

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #  Создаём группу
        cls.group = Group.objects.create(
            title='group_test',
            slug='slug_test',
            description='descr_test',

        )
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
        cls.user = User.objects.create_user(username='author_test')
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post2 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post3 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post4 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post5 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post6 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post7 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post8 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post9 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post10 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post11 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post12 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

        cls.post13 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PaginatorViewsTest.post1.author)

    def test_first_page_contains_ten_records_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_index(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_group_list(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug_test'})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_group_list(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'slug_test'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'author_test'})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_profile(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'author_test'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class PostFormTests(PostForm):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )

        cls.group2 = Group.objects.create(
            title='Тесто2222вая группа',
            slug='test_slug2',
        )

        cls.user_author = User.objects.create_user(username='test-author')
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        self.post3 = Post.objects.create(
            author=PostFormTests.user_author,
            group=PostFormTests.group,
            text='Тестовый без группы пост',
        )
        # Подсчитаем количество записей в Posts
        tasks_count = Post.objects.count()

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_data = {
            'text': 'Новый текст поста',
            'group': PostFormTests.group2,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_create'))

    #     # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)




