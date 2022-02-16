from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Категория не выбрана'

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        label = {
            'text': 'Содержание',
            'group': 'Группа',
            'image': 'Картиночка'
        }
        help_text = {
            'text': 'Текст поста',
            'group': 'Группа,к которой будет относиться пост',
            'image': 'Можешь добавить мемасы',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        label = {
            'text': 'Содержание комментария',
        }
