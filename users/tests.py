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

    def test_PageProfile(self):
        response = self.client.get("/sarah/")
        self.assertEqual(response.status_code, 200)
    
    def test_AuthorizationUserPosting(self):
        self.client.login(username='sarah', password='12345678')
        self.client.post("/new/", {"text": self.test_post})
        response = self.client.get("/")
        self.assertContains(response, self.test_post)

    def test_UnAuthorizedUserCannotPost(self):
        #self.client.logout() # Не нужно разлогиневаться так как при переходе на новый тест я автоматом разлогинелся
        response = self.client.get('/new/')
        self.assertRedirects(response, '/')

    def test_NewPostAppearOnDesiredPages(self):

        new = Post.objects.create(author=self.user, text= self.test_post)
        
        response = self.client.get("/")
        self.assertContains(response, self.test_post)

        response = self.client.get("/sarah/")
        self.assertContains(response, self.test_post)

        response = self.client.get(f"/sarah/{new.id}/")
        self.assertContains(response, self.test_post)

    def test_EditingEndCheckingLinkedPages(self):
        self.client.login(username='sarah', password='12345678') # Логинюсь
        #response = self.client.get('/new/', follow=True)

        new = Post.objects.create(author=self.user, text= self.test_post) # Создаю пост
        #response = self.client.get(f"/sarah/{new.id}/edit")
        self.client.post(f"/sarah/{new.id}/edit", {"text": "modified"}) # Редактирую пост

        self.assertEqual(Post.objects.get(author=self.user).text, "modified") # Изменился ли пост?

       
        


    


