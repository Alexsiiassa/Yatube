from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Comment


User = get_user_model()


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='ArtComms')
        cls.group = Group.objects.create(
            title='Название группы для теста3',
            slug='test-slug3',
            description='Описание группы для теста3'
        )
        cls.post = Post.objects.create(
            text='Текст поста для теста3',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст коммента для теста',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Валидная форма создает комментарий."""
        form_data = {
            'text': 'Текст коммента для теста',
            'post': self.post,
        }
        # Отправили POST запрос
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        # Проверили редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        # Проверили, что коммент создан
        self.assertTrue(
            Comment.objects.filter(
                text='Текст коммента для теста',
                post=self.post
            ).exists()
        )
