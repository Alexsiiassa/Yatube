from django.conf import settings
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

    def test_auth_follow(self):
        """ Авторизованный пользователь подписывается на других
            и удалять их из подписок.
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

        self.response_post(
            'posts:profile_unfollow',
            rev_args={'username': following}
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            False
        )

    def test_new_post(self):
        """ Новая запись появляется в ленте тех, кто подписан
        и не появляется в ленте, кто не подписан.
        """
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.text)
        response = self.response_get('posts:follow_index')
        self.assertIn(post, response.context['page_obj'].object_list)

        self.client.logout()
        User.objects.create_user(
            username='somebody_2',
            password='pass'
        )
        self.client.login(username='somebody_2', password='pass')
        response = self.response_get('posts:follow_index')
        self.assertNotIn(post, response.context['page_obj'].object_list)

    def test_auth_comments(self):
        """ Только авторизованный пользователь может комментировать посты.
        """
        post = Post.objects.create(author=self.user, text=self.text)
        comment = 'comment text'
        self.response_post(
            'posts:add_comment',
            rev_args={
                'username': self.user.username,
                'post_id': post.id
            },
            post_args={'text': comment}
        )
        response = self.response_get(
            'post',
            rev_args={
                'username': self.user.username,
                'post_id': post.id
            }
        )
        self.assertContains(response, comment)

        self.client.logout()
        response = self.response_post(
            'posts:add_comment',
            rev_args={
                'username': self.user.username,
                'post_id': post.id
            },
            post_args={'text': comment}
        )
        reverse_string = reverse(
            'posts:add_comment',
            kwargs={
                'post_id': post.id,
                'username': self.user.username
            }
        )
        redirect_string = f"{settings.LOGIN_URL}?next={reverse_string}"
        self.assertRedirects(
            response,
            redirect_string
        )
