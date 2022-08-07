# posts/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group
        )

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
        self.authorized_client.force_login(self.user_author)

        # self.post = Post.objects.create(
        #     author=PostPagesTests.user_author,
        #     group=PostPagesTests.group,
        #     text='Тестовый пост',
        # )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"

        templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            PROFILE_URL: 'posts/profile.html',
            GROUP_URL: 'posts/group_list.html',
            CREATE_POST_URL: 'posts/create_post.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
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
            'text': 'text_test_cod11',
            'group': f'{self.post.group.id}',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, PROFILE_URL)
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась новая запись
        # Данные последней записи совпадают с тестовыми
        last_post = Post.objects.order_by('pk').last()
        expected_post_text = form_data['text']
        expected_post_group = int(form_data['group'])
        self.assertEqual(last_post.text, expected_post_text)
        self.assertEqual(last_post.group_id, expected_post_group)

    def test_edit_post(self):
        """Валидная форма редактирует Пост в БД."""
        form_data = {
            'text': 'text_test357',
            'group': f'{self.post.group.id}',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, (self.POST_DETAIL_URL))
        # Проверяем, что пост отредактирован
        self.assertTrue(
            Post.objects.filter(
                text='text_test357',
                group=self.group.id
            ).exists()
        )
