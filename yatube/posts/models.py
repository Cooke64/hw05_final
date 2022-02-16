from django.contrib.auth import get_user_model
from django.db import models


from core.models import CreatedModel
User = get_user_model()


class Post(CreatedModel, models.Model):
    text = models.TextField(
        'Текст публикации',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
        default=1
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        blank=True
    )
    slug = models.SlugField(
        'URL',
        unique=True
    )
    description = models.TextField(
        'Описание',
        blank=True
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/group/{self.slug}/'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        related_name='comments',
        null=True,
        blank=True,
        verbose_name='Пост'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='comments',
        null=True,
        blank=True,
        verbose_name='Автор'
    )
    text = models.TextField(
        'Текст комментария',
        null=True,
    )
    created = models.DateTimeField(
        'Дата публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
        null=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
        null=True
    )
