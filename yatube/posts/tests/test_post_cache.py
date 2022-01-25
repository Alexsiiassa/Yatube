from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostsCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='somebody')
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_home_page(self):
        """Тестируем удаление записи и кеш"""
        post_count = Post.objects.all().count()
        print("before", post_count)
        response_before = self.authorized_client.get(reverse("posts:index"))
        content_before = response_before.content
        Post.objects.get(pk=1).delete()
        response_after = self.authorized_client.get(reverse("posts:index"))
        content_after = response_after.content
        post_count = Post.objects.all().count()
        print("after", post_count)
        self.assertEqual(content_before, content_after)
