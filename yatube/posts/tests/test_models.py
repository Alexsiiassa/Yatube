from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='somebody')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-descriptipon',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-group',
        )

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у моделей корректно работает __str__ для Post."""
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей корректно работает __str__ для Group."""
        self.assertEqual(str(self.group), self.group.title)
