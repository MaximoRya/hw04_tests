from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()

# Create your tests here.

class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345678")
        self.test_post = "Test post from sarah"

    def test_Page_Profile(self):
        response = self.client.get("/sarah/")
        self.assertEqual(response.status_code, 200)

    """
    URL'ы в тестах можно генерировать по namespac'ам. Например:
    url = reverse('archive', args=[1988])
    assertEqual(url, '/archive/1988/')
    Тем самым, если изменится url, можно будет править тесты 

    Подскажите, пожалуйста, как этим воспользоваться в test_Page_Profile?
    """
    
    def test_Authorization_User_Posting(self):
        self.client.login(username='sarah', password='12345678')
        self.client.post("/new/", {"text": self.test_post})
        response = self.client.get("/")
        self.assertContains(response, self.test_post)

    def test_Unauthorized_User_Cannot_Post(self):
        #self.client.logout() # Не нужно разлогиневаться так как при переходе на новый тест я автоматом разлогинелся
        response = self.client.get('/new/')
        self.assertRedirects(response, '/')

    def test_New_Post_Appear_On_Desired_Pages(self):

        new = Post.objects.create(author=self.user, text= self.test_post)
        
        response = self.client.get("/")
        self.assertContains(response, self.test_post)

        response = self.client.get("/sarah/")
        self.assertContains(response, self.test_post)

        response = self.client.get(f"/sarah/{new.id}/")
        self.assertContains(response, self.test_post)

    def test_Editing_End_Checking_Linked_Pages(self):

        self.client.login(username='sarah', password='12345678') # Логинюсь
        new = Post.objects.create(author=self.user, text= self.test_post) # Создаю пост
        self.client.post(f"/sarah/{new.id}/edit", {"text": "modified"}) # Редактирую пост
        self.assertEqual(Post.objects.get(author=self.user).text, "modified") # Изменился ли пост

       
        


    





# from django.test import TestCase
# from django.test import Client

# # Create your tests here.

# class TestStringMethods(TestCase):
#         def test_length(self):
#                 self.assertEqual(len("yatube"), 6)

#         def test_show_msg(self):
#                 # действительно ли первый аргумент — True?
#                 self.assertTrue(False, msg="Важная проверка на истинность")

# class ProfileTest(TestCase):
#         def setUp(self):
#                 # создание тестового клиента — подходящая задача для функции setUp()
#                 self.client = Client()
#                 # создаём пользователя
#                 self.user = User.objects.create_user(
#                         username="sarah", email="connor.s@skynet.com", password="12345"
#                 )
#                 # создаём пост от имени пользователя
#                 self.post = Post.objects.create(text="You're talking about things I haven't done yet in the past tense. It's driving me crazy!", author=self.user)

#         def test_profile(self):
#                 # формируем GET-запрос к странице сайта
#                 response = self.client.get("/sarah/")

#                 # проверяем что страница найдена
#                 self.assertEqual(response.status_code, 200)

#                 # проверяем, что при отрисовке страницы был получен список из 1 записи
#                 self.assertEqual(len(response.context["posts"]), 1)

#                 # проверяем, что объект пользователя, переданный в шаблон, 
#                 # соответствует пользователю, которого мы создали
#                 self.assertIsInstance(response.context["profile"], User)
#                 self.assertEqual(response.context["profile"].username, self.user.username)
