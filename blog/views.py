# -*- codding: utf-8 -*-
import re
import time
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.defaults import page_not_found
from django.http import Http404
from .models import Post, PostCategory, Comment, Profile
from .forms import AddPostForm, AddComment, UpdateProfileForm, UpdateUserForm, RegisterForm #, AuthenticationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from chat.views import  unread_msg_num
# Create your views here.
def paginate(request, posts):
    page = request.GET.get('page')
    paginator = Paginator(posts, 2)
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)
    return posts_page


def main_page(request):
    if request.user.is_authenticated:
        posts = Post.objects.all().order_by('published_date')
    else: posts = ""
    categories = PostCategory.objects.all()
    posts = paginate(request, list(posts))
    msg_num = unread_msg_num(request)
    context = {
        'posts': posts,
        'sidebar': categories,
        'msg_num': msg_num
    }
    return render(request, 'main_page.html', context)
def index(request):
    return render(request, 'index.html')

def add_post(request):
    add_post_form=None
    if request.user.is_authenticated:
        if request.method == "POST":
            add_post_form = AddPostForm(request.POST, request.FILES)
            if add_post_form.is_valid():
                print("Valid!")
                url = request.POST.get('post_slug')
                new_post = add_post_form.save()
                new_post.save()
                print(url)
                return redirect(f"/{url}")
            else: 
                print("unValid!")
        else:
            add_post_form = AddPostForm()
    context = {
        'post_form': add_post_form
    }
    return render(request, 'add_post.html', context)
@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, 
                                        instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile was successfully updated!')
            return redirect(to = 'user_profile')
    else:
            user_form = UpdateUserForm(instance=request.user)
            profile_form = UpdateProfileForm(instance=request.user.profile)
    profile = request.user.profile
    return render(request, 'profile.html', {
        'profile' : profile,
        'user_form' : user_form,
        'profile_form' : profile_form
    })
def look_profile(request, profile):
    profile = Profile.objects.get(user__username=profile)
    if profile == request.user.profile:
        return redirect(to = 'user_profile')
    return render(request, 'look_profile.html', {
        'profile': profile
    })
def smotri_profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, 
                                        instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile was successfully updated!')
            return redirect(to = 'user_profile')
    else:
            user_form = UpdateUserForm(instance=request.user)
            profile_form = UpdateProfileForm(instance=request.user.profile)
    profile = request.user.profile
    return render(request, 'smotri_profile.html', {
        'profile' : profile,
    })        
  

def search_post(request):
    posts = None
    if request.method == "POST":
        searched = request.POST.get('searchpost')
        posts = Post.objects.filter(title__icontains=searched)    
    sidebar = PostCategory.objects.all()
    return render(request, 
                  "search_result.html", 
                  {"sidebar": sidebar,
                   "posts": posts})

def post_comment(request, post):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddComment(request.POST or None)
            if form.is_valid():
                content = request.POST.get('content')
                comment = Comment.objects.create(post=post,
                                             author=request.user,
                                             content=content)
                comment.save()
                return redirect(f'/{post.post_slug}')
            else:
                return redirect(f'/{post.post_slug}')
        else:
            form = AddComment()
            return form


def like_post(request, pk):
    post = Post.objects.get(id=request.POST['post_id'])
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(f'/{post.post_slug}/#like_form')
def dislikes_post(request, pk):
    post = Post.objects.get(id=request.POST['post_id'])
    if post.dislikes.filter(id=request.user.id).exists():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)
    return redirect(f'/{post.post_slug}#dislike_form')
def single_slug(request, single_slug):
    sidebar = PostCategory.objects.all()
    categories = [cat.category_slug  for cat in PostCategory.objects.all()]
    if single_slug in categories:
        category_posts = Post.objects.filter(post_category__category_slug=single_slug)
        return render(request, 'category.html', {'posts':category_posts,
                      'sidebar': sidebar})
    posts_slug = [ p.post_slug for p in Post.objects.all()]
    if single_slug in posts_slug:
        post = Post.objects.get(post_slug=single_slug)
        likes_num = post.get_likes_number()
        dislikes_num = post.get_dislikes_number()
        comments = Comment.objects.filter(post=post)
        form = post_comment(request, post)
        context = {'post': post,
                   'sidebar': sidebar,
                   'comment_form': form,
                   'comments': comments,
                   'likes_num': likes_num,
                   'dislikes_num': dislikes_num,}
        return render(request, 'post_view.html', context)
    else:
        raise Http404
        #page_not_found(request, 'Article not found!')


def register(request):
    if request.method =="POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("Sucsess IN REGISTER!!!")
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("/")
        else:
            print("ERRORS IN REGISTER!!!")
            for msg in form.error_messages:
                messages.error(request, f"{msg} : {form.error_messages[msg]} ")
            return render(request, 'register.html', context={'form': form})
    form = RegisterForm
    context = {'form': form}
    return render(request, 'register.html', context)
def settings(request):
    return render(request, 'settings.html')

def logout_request(request):
    logout(request)
    print("ERRORS IN REGISTER!!!")
    form = RegisterForm(request.POST)
    for msg in form.error_messages:
        messages.error(request, f"You are logged out ")
    
    return redirect("/")

def login_request(request):
    if request.method =="POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
                    
            print("Sucsess IN REGISTER!!!")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
#            email = form.cleaned_data.get("email")
            #messages.success(request, f"You are logged in: {email}")
            messages.success(request, f"You are logged in: {username}")
            user = authenticate(request, password=password , username=username)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password")
            if user is not None:
                login(request, user)
                return redirect('/')
        for msg in form.error_messages:
                messages.error(request, f"{msg} : {form.error_messages[msg]} ")
                return render(request, 'login.html', context={'form': form})

    form = AuthenticationForm()
    context = {'form': form}
    return render(request, "login.html", context)
def show_categories(request):
        categories = PostCategory.objects.all()
        msg_num =  unread_msg_num(request)
        context = {"categories": categories
                   ,"msg_num": msg_num}
        
        return render(request, "categories.html", context)


