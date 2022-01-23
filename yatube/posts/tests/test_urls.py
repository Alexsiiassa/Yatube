from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='somebody')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            pk=1
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # да помню про саб, тут просто руку набивал)

    def test_homepage(self):
        """Проверка доступности главной страницы."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about(self):
        """Проверка доступности страницы об авторе."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        """Проверка доступности страницы о технологиях."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url(self):
        """Проверка доступности страницы группы."""
        response = self.guest_client.get('/group/test-group/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_username_url(self):
        """Проверка доступности страницы пользователя."""
        response = self.authorized_client.get('/profile/somebody/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url(self):
        """Проверка доступности страницы редактирования поста."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url(self):
        """Проверка доступности страницы создания поста."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Проверка не существующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_posts_template(self):
        """URL-адреса используют правильный шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-group/',
            'posts/profile.html': '/profile/somebody/',
            'posts/post_detail.html': '/posts/1/',
            'posts/post_create.html': '/posts/1/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template, 'Шаблон не найден')

    def test_create_url_template(self):
        """Страница /added/ использует шаблон deals/added.html."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/post_create.html')
