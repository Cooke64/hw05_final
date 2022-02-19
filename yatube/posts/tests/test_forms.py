import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
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
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='22.02.2022',
            image=uploaded,
        )
        cls.form = PostForm()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_create(self):
        """Авторизованный пользователь создает пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'group': PostFormTest.group.id,
            'id': PostFormTest.post.id,
            'image': PostFormTest.post.image,
        }
        response = self.authorized_client.post(
            reverse('post:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post:profile', kwargs={'username': self.author.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                id=PostFormTest.post.id,
                text=PostFormTest.post.text,
                group=PostFormTest.group.id,
                image=PostFormTest.post.image,
            ).exists()
        )

    def test_no_authorized_person_cant_create_post(self):
        """Не авторизованный пользователь
        не может создать пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'group': PostFormTest.group.id,
            'id': PostFormTest.post.id,
            'image': PostFormTest.post.image,
        }
        response_1 = self.guest_client.post(
            reverse('post:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_1, ('/auth/login/?next=/create/'))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                id=PostFormTest.post.id,
                text=PostFormTest.post.text,
                group=PostFormTest.group.id,
                image=PostFormTest.post.image,
            ).exists()
        )

    def test_post_edit(self):
        """При отправке валидной формы пост редактируется."""
        text_edit = 'Отредактированный текст'
        posts_count = Post.objects.count()
        form_data = {
            'text': text_edit,
            'group': PostFormTest.group.id,
        }
        response_1 = self.authorized_client.post(
            reverse('post:post_edit',
                    kwargs={'post_id': PostFormTest.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_1, reverse(
            'post:post_detail', kwargs={'post_id': PostFormTest.post.id}), )

        self.assertTrue(Post.objects.filter(
            group=PostFormTest.group.id,
            id=PostFormTest.post.id,
            text=text_edit,
        ).exists())
        self.assertEqual(Post.objects.count(), posts_count)

    def test_no_authorized_person_cant_edit_post(self):
        """Не авторизованный пользователь
        не может редактировать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'group': PostFormTest.group.id,
            'image': PostFormTest.post.image,
        }
        response = self.guest_client.post(
            reverse('post:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (
            '/auth/login/?next=%2Fposts%2F1%2Fedit%2F'))
        self.assertEqual(Post.objects.count(), posts_count)

    def test_form_create_comment(self):
        """Валидная форма создает комментарий."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Comment'
        }
        response = self.authorized_client.post(
            reverse(
                'post:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post:post_detail', kwargs={
                'post_id': PostFormTest.post.pk}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Comment',
            ).exists()
        )
