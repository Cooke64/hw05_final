from django.test import TestCase

from ..models import Group, Post, User, Follow, Comment


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.user = User.objects.create_user(username='just_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Очень длинный текст',
            pub_date='22.02.2022',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Очень плохой коммент',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_all_models_have_correct_object_names(self):
        """Проверяем, что у модели Post
        and Group корректно работает __str__."""
        # Модель Post
        self.assertEqual(str(self.post), self.post.text[:15])
        # Модель Group
        self.assertEqual(str(self.group), self.group.title)
        # Модель Comment
        self.assertEqual(str(self.comment), self.comment.text[:15])
        # Модель Follow
        username_author = self.follow.author.username
        username_user = self.follow.user.username
        self.assertEqual(str(self.follow),
                         f'{username_user}, {username_author}')

    def test_verbose_name_post_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post_text = PostModelTest.post
        field_verboses = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post_text._meta.get_field(field).verbose_name,
                    expected_value)

    def test_verbose_name_group_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'URL',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_comment_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verbose = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации комментария'
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value)

    def test_verbose_name_follow_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = PostModelTest.follow
        field_verbose = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value)
