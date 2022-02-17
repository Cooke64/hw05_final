from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView

from .forms import PostForm, CommentForm
from .models import Post, User, Group, Comment, Follow

AMOUNT_POST = 10


class IndexView(ListView):
    model = Post
    template_name = 'posts/index.html'
    paginate_by = AMOUNT_POST

    def get_queryset(self):
        return Post.objects.all().order_by('-pub_date')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    counter_posts = author.posts.count()
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'counter_posts': counter_posts,
        'following': following

    }
    return render(request, 'posts/profile.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    get_posts = Post.objects.filter(group=group)
    posts = get_posts.order_by('-pub_date')[:AMOUNT_POST]
    paginator = Paginator(posts, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def post_detail(request, post_id):
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    username_obj = User.objects.get(username=post.author)
    posts_counter = username_obj.posts.count()
    context = {
        'post': post,
        'posts_counter': posts_counter,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        self.post = form.save(commit=False)
        self.post.author = self.request.user
        self.post.save()
        return redirect('post:profile', username=self.request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('post:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    # Добавляем комментарий
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # Выводит все посты автора,на которых подписан пользователь
    # фильтрация по полям user,following,author
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    paginator = Paginator(posts, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request,
                  "posts/follow.html",
                  context
                  )


@login_required
def profile_follow(request, username):
    # Подписаться на автора.
    follow = get_object_or_404(User, username=username)
    is_exist = Follow.objects.filter(user=request.user, author=follow).exists()
    if follow != request.user and not is_exist:
        Follow.objects.get_or_create(
            user=request.user,
            author=follow
        )
    return redirect('post:profile', follow)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка.
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    # Проверка по заданным условиям.
    # В случае аличия,удаляется запись из бд
    if follow.exists():
        follow.delete()
    return redirect('post:profile', username=username)
