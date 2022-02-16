from django.urls import path

from . import views

app_name = 'post'

urlpatterns = [
    path('', views.IndexView.as_view(), name='main'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('create/', views.PostCreateView.as_view(), name='create'),
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'
