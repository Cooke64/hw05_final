from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User, Follow, Comment


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.user = User.objects.create_user(username='user')
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
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.new_group = Group.objects.create(
            title='Тестовый заголовок 1',
            slug='test_slug_1',
            description='Тестовый текст 1',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='22.02.2022',
            image=uploaded,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый текст'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('post:main'),
            'posts/group_list.html': (
                reverse('post:group', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('post:profile', kwargs={'username': 'test_user'})
            ),
            'posts/post_detail.html': (
                reverse('post:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': (
                reverse('post:post_edit', kwargs={'post_id': '1'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue('is_edit' in response.context)

    def test_post_index_page_show_correct_context(self):
        """Проверяем Context страницы index"""
        response = self.authorized_client.get(reverse('post:main'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_posts_groups_page_show_correct_context(self):
        """Проверяем Context страницы posts_groups"""
        response = self.authorized_client.get(
            reverse('post:group', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_profile_page_show_correct_context(self):
        """Проверяем Context страницы profile"""
        response = self.authorized_client.get(
            reverse('post:profile', kwargs={'username': self.author.username}))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post:create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_profile_page_list_is_1(self):
        """В шаблон profile передается верное количество постов"""
        response = self.authorized_client.get(
            reverse('post:profile',
                    kwargs={'username': ViewsTests.post.author}))
        object_all = response.context['page_obj']
        self.assertEqual(len(object_all), 1)

    def test_post_new_create_appears_on_correct_pages(self):
        """При создании поста он должен появляется на главной странице,
        на странице выбранной группы и в профиле пользователя"""
        exp_pages = [
            reverse('post:main'),
            reverse(
                'post:group', kwargs={'slug': self.group.slug}),
            reverse(
                'post:profile', kwargs={'username': self.author.username})
        ]
        for revers in exp_pages:
            with self.subTest(revers=revers):
                response = self.authorized_client.get(revers)
                self.assertIn(self.post, response.context['page_obj'])

    def test_posts_not_contain_in_wrong_group(self):
        """При создании поста он не появляется в другой группе"""
        post = Post.objects.get(pk=1)
        response = self.authorized_client.get(
            reverse('post:group', kwargs={'slug': self.new_group.slug})
        )
        self.assertNotIn(post, response.context['page_obj'].object_list)

    def test_caching_main_page_correct(self):
        """Проверка кеширования главной страницы"""
        cache.clear()
        response = self.authorized_client.get(reverse('post:main'))
        posts_count = Post.objects.count()
        self.post.delete
        self.assertEqual(len(response.context['page_obj']), posts_count)
        cache.clear()
        posts_count = Post.objects.count()
        self.assertEqual(len(response.context['page_obj']), posts_count)

    def test_comment_make_only_one_item(self):
        """в базе создается объект comment и только один"""
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                author=self.user,
                text='Тестовый текст'
            ).exists
        )
        response = Comment.objects.filter(
            post=self.post,
            author=self.user,
            text='Тестовый текст'
        ).count()
        self.assertEqual(response, 1)

    def test_comment_context_of_post_detail_is_correct(self):
        """Шаблон post_detail сформирован с правильными комментариями"""
        response = self.authorized_client_1.get(
            reverse('post:post_detail', args={self.post.pk}))
        comments = response.context['comments'][0]
        expected_fields = {
            comments.author.username: 'user',
            comments.post.id: self.post.id,
            comments.text: 'Тестовый текст'
        }
        for fields, values in expected_fields.items():
            with self.subTest(expected_fields=expected_fields):
                self.assertEqual(fields, values)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        # bulk_create для создания
        # 13 объектов модели Post
        objs = [
            Post(
                author=cls.author,
                group=cls.group,
                text='Тестовый заголовок',
                pub_date='22.02.2022',
            )
            for bulk in range(1, 14)
        ]
        cls.post = Post.objects.bulk_create(objs)

    def test_first_page_contains_ten_records(self):
        """Проверка: на первой странице должно быть 10 постов."""
        response = self.client.get(reverse('post:main'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('post:main') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_contains_ten_pages(self):
        """Проверка: на  странице group_list должно быть 10 постов."""
        response = self.client.get(
            reverse('post:group', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_contains_ten_records(self):
        """Проверка: на  странице рофиля должно быть 10 постов."""
        response = self.client.get(reverse(
            'post:profile', kwargs={'username': self.author.username}))
        self.assertEqual(len(response.context['page_obj']), 10)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

    def setUp(self):
        self.follow = Follow.objects.get_or_create(
            user=self.follower,
            author=self.author
        )

    def test_follow_index_context_coorect(self):
        """Шаблон follow_index сформирован с правильным контекстом """
        response = self.follower_client.get(reverse('post:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        self.assertEqual = (post_author_0, 'author')
        post_text_0 = first_object.text
        self.assertEqual = (post_text_0, 'Тестовый текст')

    def test_follow_make_only_one_item(self):
        """В бд создается только один объект """
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower.is_authenticated, author=self.author,
            ).exists()
        )
        response = Follow.objects.filter(
            user=self.follower.is_authenticated, author=self.author,
        ).count()
        self.assertEqual(response, 1)

    def test_unfollow_delete_item_out_db(self):
        """После отписки объект follow удаляется из базы"""
        Follow.objects.filter(
            user=self.follower.is_authenticated, author=self.author,
        ).delete()
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower.is_authenticated, author=self.author,
            ).exists()
        )

    def test_follow_index_context_delete_author_from_index(self):
        """Шаблон follow_index после удаления подписки убирает посты автора"""
        Follow.objects.filter(
            user=self.follower.is_authenticated, author=self.author,
        ).delete()
        response = self.follower_client.get(reverse('post:follow_index'))
        self.assertEqual = (len(response.context['page_obj']), 0)
