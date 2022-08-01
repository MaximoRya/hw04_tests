"""Файл для отправки и отображения информации из баз в шаблоны."""
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import PostForm

from .models import Group, Post, User


def index(request):
    """Метод для отображения информации  на главной странице."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
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
    paginator = Paginator(post_list, 10)
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
        Post.objects.filter(author__username=username).order_by('-pub_date')
    )
    posts_count = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'posts_count': posts_count,
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


@login_required
def post_create(request):
    form = PostForm(request.POST)

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
    form = PostForm(request.POST, instance=post)
    if request.method == 'GET':
        return render(request, 'posts/create_post.html',
                      {'post_list': post_list,
                       'post': post,
                       'is_edit': True,
                       'form': form,
                       'post_id': post_id,
                       })
    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {'post_id': post_id,
               'form': form,
               'post': post,
               'is_edit': True
               }
    return render(request, 'posts/create_post.html', context)
