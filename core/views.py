from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages  
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Story, StoryComment,Comment
from itertools import chain
import random
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the old password is correct
        if not request.user.check_password(old_password):
            messages.error(request, 'Incorrect current password.')
            return redirect('settings')

        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('settings')

        # Check if new password is provided (simple check)
        if not new_password:
             messages.error(request, 'Please provide a new password.')
             return redirect('settings')

        # Set the new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Important: Keep the user logged in after password change
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password updated successfully.')
        return redirect('settings')
    
    return redirect('settings')

# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Get following users and add current user to list
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    user_following_list = [user.user for user in user_following]
    user_following_list.append(request.user.username)
    
    # Get posts from following users and own posts, ordered by newest first
    feed_list = Post.objects.filter(user__in=user_following_list).order_by('-created_at')
    
    # Check if user liked the post
    feed_list = list(feed_list)
    for post in feed_list:
        post.user_liked = LikePost.objects.filter(post_id=post.id, username=request.user.username).exists()
        
    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = User.objects.filter(username__in=user_following_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list =[ x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    # Get active stories
    active_stories = Story.objects.filter(created_at__gt=timezone.now() - timedelta(hours=24))
    story_users = set(active_stories.values_list('user', flat=True))
    
    # Get IDs of stories viewed by current user
    viewed_story_ids = set(request.user.viewed_stories.values_list('id', flat=True))

    # Include current user and followed users
    relevant_users = set(user_following_list + [request.user.username])
    stories_data = []
    for user in story_users:
        if user in relevant_users:
            user_stories = active_stories.filter(user=user)
            user_profile_story = Profile.objects.filter(user__username=user).first()
            
            has_unseen = False
            if user == request.user.username:
                has_unseen = True
            else:
                has_unseen = user_stories.exclude(id__in=viewed_story_ids).exists()

            stories_data.append({
                'user': user,
                'profile_img': user_profile_story.profileimg.url if user_profile_story else '',
                'stories': list(user_stories),
                'has_unseen': has_unseen
            })

    
    return render(request, 'index.html', { 'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4], 'stories': stories_data})


@login_required(login_url='signin')
def upload(request):
    
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption= request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)


    if request.method == 'POST':
       username = request.POST['username']
       username_object = User.objects.filter(username__icontains=username)

       username_profile = []
       username_profile_list = []

       for users in username_object:
            username_profile.append(users.id)


       for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

    username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def like_post(request):

    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk).order_by('-created_at')
    user_posts_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def post_comment(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')
        
        if post_id and comment_text:
            post = Post.objects.get(id=post_id)
            Comment.objects.create(post=post, user=request.user, text=comment_text)
            
    return redirect('/') # Redirects back to the home page

@login_required(login_url='signin')
def delete_comment(request):
    comment_id = request.GET.get('id')
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
        comment.delete()
    except Comment.DoesNotExist:
        pass # Handle error or ignore if comment doesn't exist/user not owner
    return redirect('/')




@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user= user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)


    else:
        return redirect('/')




@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
           if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
           elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
           else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a profile object for the new 
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
                
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    else:

        return render(request, 'signup.html')


def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user= auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
        
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')    
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def upload_story(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('story_image')
        video = request.FILES.get('story_video')
        caption = request.POST.get('caption', '')
        music = request.FILES.get('story_music')

        new_story = Story.objects.create(user=user, image=image, video=video, caption=caption, music=music)
        new_story.save()
        messages.info(request, 'Story uploaded successfully!')
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def get_stories(request):
    active_stories = Story.objects.filter(created_at__gt=timezone.now() - timedelta(hours=24))
    # Get unique users who have active stories
    story_users = active_stories.values_list('user', flat=True).distinct()
    stories_data = []
    for user in story_users:
        user_stories = active_stories.filter(user=user)
        user_profile = Profile.objects.filter(user__username=user).first()
        stories_data.append({
            'user': user,
            'profile_img': user_profile.profileimg.url if user_profile else '',
            'stories': user_stories
        })
    return JsonResponse({'stories': stories_data})


@login_required(login_url='signin')
def view_story(request, story_id):
    story = Story.objects.get(id=story_id)
    user = request.user
    story_author_profile = Profile.objects.get(user__username=story.user)
    
    if story.user != user.username:
        if not story.viewers.filter(id=user.id).exists():
            story.viewers.add(user)
            story.views += 1
        story.save()

    comments = StoryComment.objects.filter(story=story).order_by('created_at')
    comments_data = []
    for comment in comments:
        comments_data.append({
            'user': comment.user,
            'comment': comment.comment,
            'created_at': comment.created_at.isoformat()
        })
    
    response_data = {
        'story': {
            'id': str(story.id),
            'user': story.user,
            'user_profile_img': story_author_profile.profileimg.url,
            'image': story.image.url if story.image else None,
            'video': story.video.url if story.video else None,
            'caption': story.caption,
            'music': story.music.url if story.music else None,
            'created_at': story.created_at.isoformat(),
            'views': story.views
        },
        'comments': comments_data
    }

    if story.user == user.username:
        viewers_data = []
        for viewer in story.viewers.all():
            try:
                profile = Profile.objects.get(user=viewer)
                img_url = profile.profileimg.url
            except Profile.DoesNotExist:
                img_url = ''
            viewers_data.append({
                'username': viewer.username,
                'profile_img': img_url
            })
        response_data['story']['viewers'] = viewers_data

    return JsonResponse(response_data)


@login_required(login_url='signin')
def add_story_comment(request, story_id):
    if request.method == 'POST':
        story = Story.objects.get(id=story_id)
        user = request.user.username
        comment = request.POST['comment']
        new_comment = StoryComment.objects.create(story=story, user=user, comment=comment)
        new_comment.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required(login_url='signin')
def delete_story(request, story_id):
    if request.method == 'POST':
        try:
            story = Story.objects.get(id=story_id)
            if request.user.username == story.user:
                story.delete()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        except Story.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Story not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url='signin')
def delete_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    try:
        post = Post.objects.get(id=post_id)
        if post.user == username:
            post.delete()
    except Post.DoesNotExist:
        pass

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='signin')
def edit_post(request):
    post_id = request.GET.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return redirect('/')

    if request.method == 'POST':
        if post.user == request.user.username:
            post.caption = request.POST.get('caption')
            post.save()
            return redirect('/')
    
    return render(request, 'edit_post.html', {'post': post})