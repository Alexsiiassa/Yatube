from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_posts_page(self):
        """Страницы author, tech доступны любому пользователю."""
        url_names = {
            reverse('about:author',): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_about_template(self):
        """URL-адреса используют правильный шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template, 'Шаблон не найден')
