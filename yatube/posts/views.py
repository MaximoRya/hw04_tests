"""Файл для отправки и отображения информации из баз в шаблоны."""
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import PostForm, CommentForm
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .models import Follow, Group, Post, User, Comment

from yatube.settings import COUNT_POST_FOR_PAGE

@cache_page(60 * 15, key_prefix='index_page')
def index(request):
    """Метод для отображения информации  на главной странице."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, COUNT_POST_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': post_list,
        'year': datetime.now().year,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Метод для отображения всех других страниц кроме главной."""
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all()
    paginator = Paginator(post_list, COUNT_POST_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'post_list': post_list,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = (
        Post.objects.filter(author__username=username)
    )
    paginator = Paginator(posts, COUNT_POST_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'author': user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.select_related('author').filter(
        author=post.author).count()
    context = {
        'post': post,
        'post_count': post_count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = Comment.objects.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.user.is_authenticated:

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post_list = Post.objects.all()
    post = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostForm(
        request.POST,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'GET':
        return render(request, 'posts/create_post.html',
                      {'post_list': post_list,
                       'post': post,
                       'is_edit': True,
                       'form': form,
                       'post_id': post_id,
                       })
    form = PostForm(
        request.POST,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {'post_id': post_id,
               'form': form,
               'post': post,
               'is_edit': True
               }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    list_of_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(list_of_posts, COUNT_POST_FOR_PAGE)
    page_namber = request.GET.get('page')
    page_obj = paginator.get_page(page_namber)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user=request.user
    author=User.objects.get(username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username)
# def profile_follow(request, username):
#     user = request.user
#     author = User.objects.get(username=username)
#     is_follower = Follow.objects.filter(user=user, author=author)
#     if user != author and not is_follower.exists():
#         Follow.objects.filter(user=request.user, author=author)
#     return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)