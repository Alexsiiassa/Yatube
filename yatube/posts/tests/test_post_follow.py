from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post

User = get_user_model()


class TestFinal(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='somebody', password='pass'
        )
        self.user.save()
        self.client.login(username='somebody', password='pass')
        self.text = "test text about"

    def response_get(self, name, rev_args=None, followed=True):
        return self.client.get(
            reverse(
                name,
                kwargs=rev_args
            ),
            follow=followed
        )

    def response_post(self, name, post_args=None, rev_args=None, fol=True):
        return self.client.post(
            reverse(
                name,
                kwargs=rev_args
            ),
            data=post_args,
            follow=fol
        )

    def test_auth_follow_add(self):
        """ Авторизованный пользователь подписывается на других.
        """
        following = User.objects.create(username='following')
        self.response_post(
            'posts:profile_follow',
            rev_args={'username': following}
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            True
        )

    def test_auth_follow_dell(self):
        """ Авторизованный пользователь удаляет из подписок.
        """
        following = User.objects.create(username='following')
        self.response_post(
            'posts:profile_unfollow',
            rev_args={'username': following}
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            False
        )

    def test_new_post(self):
        """ Новая запись появляется в ленте тех, кто подписан.
        """
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.text)
        response = self.response_get('posts:follow_index')
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_new_post_invisible(self):
        """ Новая запись не появляется в ленте, кто не подписан.
        """
        following = User.objects.create(username='following')
        post = Post.objects.create(author=following, text=self.text)
        self.client.logout()
        User.objects.create_user(
            username='somebody_2',
            password='pass'
        )
        self.client.login(username='somebody_2', password='pass')
        response = self.response_get('posts:follow_index')
        self.assertNotIn(post, response.context['page_obj'].object_list)
