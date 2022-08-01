# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #  Создаём группу
        cls.group = Group.objects.create(
            title='group_test',
            slug='slug_test',
            description='descr_test',

        )
        # Создадим запись в БД для проверки доступности адресов страниц
        cls.user = User.objects.create_user(username='author_test')
        cls.post = Post.objects.create(
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
        self.authorized_client.force_login(PostURLTests.post.author)

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        """Страница Profile доступна любому пользователю"""
        post_author = self.post.author
        response = self.guest_client.get(f'/profile/{post_author}/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        """Страница Post_detail доступна любому пользователю"""
        post_id = self.post.pk
        response = self.guest_client.get(f'/posts/{post_id}/')
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        """Страница Group доступна любому пользователю"""
        group_slug = self.post.group.slug
        response = self.guest_client.get(f'/group/{group_slug}/')
        self.assertEqual(response.status_code, 200)

    # Проверка кода 404 для несуществующих страниц
    def test_unexisting(self):
        """Несуществующая страница выдаёт код 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    # Проверка доступа к созданию нового поста для авторизованного пользователя
    def test_create(self):
        """Страница Create доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        """Страница редактирования доступна автору поста"""
        post_id = self.post.pk
        response = self.authorized_client.get(f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_home_url_uses_correct_template(self):
        """Страница по адресу / использует шаблон posts/index.html."""
        response = self.authorized_client.get('/')
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        group_slug = self.post.group.slug
        post_author = self.post.author
        post_id = self.post.pk
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group_slug}/': 'posts/group_list.html',
            f'/profile/{post_author}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template, in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_uses_correct_template(self):
        """URL-адрес редактирования использует соответствующий шаблон."""
        post_id = self.post.pk
        response = self.authorized_client.get(f'/posts/{post_id}/edit/')
        self.assertTemplateUsed(
            response, 'posts/create_post.html', 'author_edit_post_error'
        )
