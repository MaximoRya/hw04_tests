# posts/tests/test_views.py
from genericpath import exists
from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User, Comment

from yatube.settings import COUNT_POST_FOR_PAGE

TEST_AUTOR = 'author_test'
GROUP_SLUG = 'slug_test'
INDEX_URL = reverse('posts:index')
GROUP_URL = reverse(
    'posts:group_list', kwargs={'slug': GROUP_SLUG}
)
PROFILE_URL = reverse(
    'posts:profile', kwargs={'username': TEST_AUTOR}
)
CREATE_POST_URL = reverse('posts:post_create')


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author_test')
        cls.guest = User.objects.create_user(username='guest')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_test',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            image=uploaded,
            pub_date='14.07.2022',
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.author,
            image=uploaded,
            pub_date='14.07.2022',
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.form = PostForm()


        cls.form = PostForm()
        POST_ID = cls.post.id
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': POST_ID}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', kwargs={'post_id': POST_ID}
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostPagesTests.post.author)
        cache.clear()
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

        self.form_data = {
            'text': 'New',
            'group': self.group.id,
            'image': uploaded
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            PROFILE_URL: 'posts/profile.html',
            GROUP_URL: 'posts/group_list.html',
            CREATE_POST_URL: 'posts/create_post.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
        }
        # Проверяем, что вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(INDEX_URL)
        context_index = response.context.get('posts')[0].text
        # Проверяем, что в посте указана группа
        self.assertIsNotNone(response.context.get('posts')[0].group)
        expected = self.post.text
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_index, expected)

    def test_group_list_page_show_correct_context(self):
        """Шаблон gruop_list сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(GROUP_URL)
        context_gruop_list_group = (
            response.context.get('page_obj')[0].group.slug
        )
        context_gruop_list_text = response.context.get('page_obj')[0].text
        expected_group = self.group.slug
        expected_text = self.post.text
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_gruop_list_group, expected_group)
        self.assertEqual(context_gruop_list_text, expected_text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        cache.clear()
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
        cache.clear()
        response = self.authorized_client.get(self.POST_EDIT_URL)
        context_post_id = response.context.get('post').id
        expected = self.post.id
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_post_id, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(CREATE_POST_URL)
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

    def test_group_list_context(self):
        """Пост не попал не в свою группу не отображается в другой группе"""
        cache.clear()
        # Формируем URL с другой группой
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
        cache.clear()
        response = self.authorized_client.get(INDEX_URL)
        context_profile_image = response.context.get('page_obj')[0].image
        expected_image = self.post_2.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_image, expected_image)

    def test_profile_image_context(self):
        """Шаблон profile сформирован с картинкой в контексте."""
        cache.clear()
        response = self.authorized_client.get(PROFILE_URL)
        context_profile_image = response.context.get('page_obj')[0].image
        expected_image = self.post_2.image
        cache.clear()
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_image, expected_image)

    def test_post_detail_image_context(self):
        """Шаблон post_detail сформирован с картинкой в контексте."""
        cache.clear()
        response = self.authorized_client.get(self.POST_EDIT_URL)
        context_profile_image = response.context.get('post').image
        expected_image = self.post.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_profile_image, expected_image)

    def test_group_image_context(self):
        """Шаблон group_list сформирован с картинкой в контексте."""
        cache.clear()
        response = self.authorized_client.get(GROUP_URL)
        context_group_list_image = response.context.get('page_obj')[0].image
        expected_image = self.post_2.image
        # Проверяем, что контекст соответствует ожиданию
        self.assertEqual(context_group_list_image, expected_image)

    def test_guest_no_comments(self):
        post = self.post
        comment_count = post.comments.count()
        
        response = self.authorized_client.get(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{post.id}'}
            ),
        )
        form_data = {
            'text': 'guest_comment',
            'author': self.author
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{post.id}'}
            ),
            data= form_data,
            follow= True
        )
        self.assertRedirects(response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{post.id}'}
            ),
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        # Проверям, что конкретный комментарий успешно добавился
        self.assertTrue(
            Comment.objects.filter(
                text= 'guest_comment',
                author= self.author
            ).exists()
        )

        comment_count = post.comments.count()
        response = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{post.id}'}
            ),
            data= form_data,
            follow= True
        )
        # Проверяем, что комментарий от гостя не добавился
        self.assertNotEqual(Comment.objects.count(), comment_count + 1)


    def test_cache_context(self):
        '''Проверка кэширования страницы index'''
        cache.clear()
        old_create_post = self.authorized_client.get(
            reverse('posts:index'))
        first_item_before = old_create_post.content
        Post.objects.create(
            author=self.author,
            text='Тестовый текст',
            group=self.group)
        after_create_post = self.authorized_client.get(reverse('posts:index'))
        first_item_after = after_create_post.content
        self.assertEqual(first_item_after, first_item_before)
        cache.clear()
        after_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_item_after, after_clear)

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
        for i in range(0, 13):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='test-text' + str(i)
            )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PaginatorViewsTest.post.author)

    def test_first_page_contains_ten_records_index(self):
        cache.clear()
        response = self.authorized_client.get(INDEX_URL)
        # Проверка: количество постов
        # на первой странице равно COUNT_POST_FOR_PAGE.
        self.assertEqual(
            len(response.context['page_obj']), COUNT_POST_FOR_PAGE
        )

    def test_second_page_contains_three_records_index(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            INDEX_URL + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_group_list(self):
        response = self.authorized_client.get(GROUP_URL)
        # Проверка: количество постов
        # на первой странице равно COUNT_POST_FOR_PAGE.
        self.assertEqual(
            len(response.context['page_obj']), COUNT_POST_FOR_PAGE
        )

    def test_second_page_contains_three_records_group_list(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            GROUP_URL + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_profile(self):
        response = self.authorized_client.get(PROFILE_URL)
        # Проверка: количество постов
        # на первой странице равно COUNT_POST_FOR_PAGE.
        self.assertEqual(
            len(response.context['page_obj']), COUNT_POST_FOR_PAGE
        )

    def test_second_page_contains_three_records_profile(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            PROFILE_URL + '?page=2'
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

        response = self.authorized_client.get(CREATE_POST_URL)
        form_data = {
            'text': 'Новый текст поста',
            'group': PostFormTests.group2,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, CREATE_POST_URL)

    #     # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower',
                                                      email='test_11@mail.ru',
                                                      password='test_pass')
        self.user_following = User.objects.create_user(username='following',
                                                       email='test22@mail.ru',
                                                       password='test_pass')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        cache.clear()
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        cache.clear()
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """запись появляется в ленте подписчиков"""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        post_text_0 = response.context["page_obj"][0].text
        self.assertEqual(post_text_0, 'Тестовая запись для тестирования ленты')
        # в качестве неподписанного пользователя проверяем собственную ленту
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(response,
                               'Тестовая запись для тестирования ленты')
