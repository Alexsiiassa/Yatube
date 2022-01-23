from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_obj = []
        cls.user = User.objects.create_user(username="auth")
        cls.group1 = Group.objects.create(
            title="test-group1",
            slug="test-slug1",
            description="test-descriptipon1",
        )
        cls.group2 = Group.objects.create(
            title="test-group2",
            slug="test-slug2",
            description="test-descriptipon2",
        )
        for i in range(1, 15):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text=f'test-text1{i}',
                    group=cls.group1,
                )
            )
        for i in range(16, 30):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text=f'test-text2{i}',
                    group=cls.group2,
                )
            )
            cls.post = Post.objects.create(
                author=cls.user,
                text='test-text11',
            )
        cls.posts_obj.append(Post(author=cls.user, text="test-text1"))
        cls.posts = Post.objects.bulk_create(cls.posts_obj)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post = Post.author

    def test_pages_correct_template(self):
        """URL-адреса использует правильный шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={
                'slug': 'test-slug1'}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': 'auth'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}),
            'posts/post_create.html': reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_correct_template(self):
        """URL-адрес используют шаблон posts/post_create.html."""
        response = self.authorized_client.\
            get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_home_page_correct_context(self):
        """Шаблон home с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_text = first_object.text
        self.assertEqual(post_text, "test-text1")

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        second_object = response.context["page_obj"][0]
        post_text_0 = second_object.text
        post_group_0 = second_object.group
        self.assertEqual(post_text_0, "test-text114")
        self.assertEqual(str(post_group_0), "test-group1")

    def test_profile_page_correct_context(self):
        """Шаблон profile с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, 'test-text1')
        self.assertEqual(post_author_0, self.user)

    def test_post_detail_page_correct_context(self):
        """Шаблон post_detail с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        self.assertEqual(
            response.context['post'].text, 'test-text11'
        )

    def test_post_create_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create',)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='somebody'
        )
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-descriptipon'
        )
        cls.post = []
        for i in range(0, 15):
            cls.post.append(Post(
                author=cls.user,
                text='test-text',
                group=cls.group
            ))
        cls.post = Post.objects.bulk_create(cls.post)

    def setUp(self):
        self.authorized_client = Client()

    def test_index_page_contains_15(self):
        """At index page - 10 posts"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_page_contains_5(self):
        """At seconf index page - 5 posts"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_list_page_contains_15(self):
        """At group_list page - 10 posts"""
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_page_contains_5(self):
        """At second group_list page - 5 posts"""
        response = self.client.get(reverse(
            ('posts:group_list'), kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_page_contains_15(self):
        """At profile page - 10 posts"""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'somebody'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_page_contains_5(self):
        """At second profile page - 5 posts"""
        response = self.client.get(reverse(
            ('posts:profile'), kwargs={'username': 'somebody'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)
