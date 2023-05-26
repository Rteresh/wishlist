from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from wish.models import Wish


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('index')  # Замените 'index' на имя вашего URL-шаблона для IndexView
        self.user1 = User.objects.create(
            username='domo',
            password='domo',
            email='domo@mail.ru'

        )
        self.user2 = User.objects.create(
            username='domo1',
            password='domo1',
            email='domo1@mail.ru'

        )

    def test_index_view_context_data(self):
        response = self.client.get(self.url)  # Выполняем GET-запрос к URL-адресу IndexView
        self.assertEqual(response.status_code, 200)  # Проверяем, что получен ответ со статусом 200 (OK)
        self.assertTemplateUsed(response, 'wish/index.html')  # Проверяем, что используется правильный шаблон
        self.assertIn('users', response.context)  # Проверяем, что в контексте ответа есть ключ 'users'
        users = response.context['users']  # Получаем значение, связанное с ключом 'users' в контексте
        self.assertEqual(users.count(), 2)  # Проверяем, что количество пользователей равно 2
        self.assertIn(self.user1, users)  # Проверяем, что user1 присутствует в списке пользователей
        self.assertIn(self.user2, users)  # Проверяем, что user2 присутствует в списке пользователей


class WishListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='domo',
            password='domo',
            email='domo@mail.ru'
        )
        self.url = reverse('wish:list_wish')

    def test_authenticated_user_can_access_wish_list(self):
        # Аутентифицируем пользователя
        self.client.login(username='domo', password='domo')

        # Отправляем GET-запрос к представлению
        response = self.client.get(self.url)

        # Проверяем, что код ответа равен 200 (успешный запрос)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в контексте передан список желаний для текущего пользователя
        self.assertQuerysetEqual(
            response.context['list_wish'],
            Wish.objects.filter(user_id=self.user.id),
            transform=lambda x: x
        )

    def test_unauthenticated_user_cannot_access_wish_list(self):
        # Отправляем GET-запрос к представлению без аутентификации
        response = self.client.get(self.url)

        # Проверяем, что код ответа равен 302 (перенаправление на страницу входа)
        self.assertEqual(response.status_code, 302)

        # Проверяем, что пользователь был перенаправлен на страницу входа
        self.assertRedirects(response, "http://127.0.0.1:8000/users/login/?next=/wish/list_wish")
