from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Follow


class FollowTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='TestAuthor'
        )
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        self.post = Post.objects.create(
            author=self.author,
            group=self.group,
            text='Очень длинный текст',
        )
        self.authorize_client = Client()
        self.authorize_client.force_login(self.user)

    def test_auth_user_can_follow(self):
        """Авторизованный пользователь может подписываться."""
        follow_count = Follow.objects.count()
        self.authorize_client.get(reverse(
            'post:profile_follow',
            kwargs={'username': self.author}))
        self.assertIs(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists(),
            True
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_auth_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться."""
        Follow.objects.create(
            user=self.user,
            author=self.author)
        self.authorize_client.get(reverse(
            'post:profile_unfollow',
            kwargs={'username': self.author}
        ))
        self.assertIs(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists(),
            False
        )

    def test_new_post_appears_in_follower_page(self):
        """Новая запись автора появляется в ленте тех, кто на него подписан."""
        Follow.objects.create(
            author=self.author,
            user=self.user
        )
        response = self.authorize_client.get(reverse('post:follow_index'))
        self.assertEqual(response.context['page_obj'][0], self.post)

    def test_new_post_doesnt_appear_in_follower_page(self):
        """Новая запись автора не появляется в ленте тех,
           кто на не него подписан."""
        follow_count = Follow.objects.count()
        Follow.objects.create(
            author=self.author,
            user=self.user
        )
        self.second_user = User.objects.create_user(
            username='username',
        )
        self.authorize_client.force_login(self.second_user)
        response = self.authorize_client.get(reverse('post:follow_index'))
        self.assertEqual(len(response.context['page_obj']), follow_count)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписаться на автора."""

        self.authorize_client.get(reverse(
            'post:profile_follow',
            kwargs={'username': self.author}))
        self.assertTrue(Follow.objects.filter(
            author=self.author,
            user=self.user).exists())
