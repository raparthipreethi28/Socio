from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.index, name='index'),
    path('settings/',views.settings, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('upload/', views.upload, name='upload'),
    path('follow/', views.follow, name='follow'),
    path('search/', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post/', views.like_post, name='like-post'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('upload-story/', views.upload_story, name='upload-story'),
    path('get-stories/', views.get_stories, name='get-stories'),
    path('view-story/<uuid:story_id>/', views.view_story, name='view-story'),
    path('add-story-comment/<uuid:story_id>/', views.add_story_comment, name='add-story-comment'),
    path('delete-story/<uuid:story_id>/', views.delete_story, name='delete-story'),
    path('delete-post/', views.delete_post, name='delete-post'),
    path('edit-post/', views.edit_post, name='edit-post'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('post-comment/', views.post_comment, name='post-comment'),
    path('delete-comment/', views.delete_comment, name='delete-comment'),

]


