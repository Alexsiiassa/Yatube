import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User1')
        cls.user_2 = User.objects.create_user(username='User2')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-group',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.redirect_profile_page = reverse(
            'posts:profile', kwargs={'username': self.post.author}
        )
        self.redirect_post_detail_page = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        )
        self.redirect_post_edit_page = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        )

    def test_post_create(self):
        """Форма создает запись в Post только авторизованным пользователем"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
            'image': uploaded
        }
        # попытка создания поста анонимом
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, self.redirect_profile_page)
        last_post = Post.objects.latest('id')

        templates_page = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            # reverse('posts:post_detail', kwargs={
            #        'post_id': f'{int(self.post.id)}'})
        ]
        for reverse_name in templates_page:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['page_obj'][1].image, self.post.image)

        self.assertTrue(
            Post.objects.filter(
                pk=last_post.pk,
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

#    def test_context_post_detail(self):
#        """Проверяем контекст post:detail"""
#        url = reverse('posts:post_detail', kwargs={'post_id': all_pages})
#        response = self.authorized_client.get(url)
#        self.assertEqual(response.status_code, HTTPStatus.OK)
#        self.assertEqual(response.context['post'], self.post)
#        self.assertEqual(response.context['post_count'], all_pages)
#        self.assertEqual(
#            self.post.image.name, 'posts/' + uploaded.name
#        )
