from django.contrib import admin
from django.contrib.auth.models import Group
from . models import Profile, Post, LikePost, FollowersCount, Story, StoryComment

# Unregister models you don't want to show in the dashboard
admin.site.unregister(Group)

# Customize how models are displayed in the list view
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'created_at', 'no_of_likes')
    search_fields = ('user', 'caption')
    list_filter = ('created_at',)

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post, PostAdmin)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Story)
admin.site.register(StoryComment)
