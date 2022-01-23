from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostsCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def test_index_cached(self):
        response = self.client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['page_obj'])
        self.post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['page_obj'])
