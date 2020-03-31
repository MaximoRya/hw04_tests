import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Post, Group, User
from .forms import PostForm

# Убрал лишнии комментарии, оставил только важные


def index(request):     
        post_list = Post.objects.order_by("-pub_date").all()
        paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
        page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
        page = paginator.get_page(page_number) # получить записи с нужным смещением

        return render(request, 'index.html', {'page': page, 'paginator': paginator})

def group_posts(request, slug):
        # функция get_object_or_404 позволяет получить объект из базы данных 
        # по заданным критериям или вернуть сообщение об ошибке если объект не найден
        group = get_object_or_404(Group, slug=slug)
        posts = Post.objects.filter(group=group).order_by("-pub_date").all() #filter - аналог WHERE group_id = {group_id}
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page') 
        page = paginator.get_page(page_number)
        return render(request, "group.html", {"group": group, "posts": posts, 'paginator': paginator, 'page': page})

def new_post(request):
        if request.user.is_authenticated : #Праверка авторизации
                if request.method == 'POST':
                        form = PostForm(request.POST)
                        if form.is_valid():
                                Post.objects.create(author=request.user, text=form.cleaned_data['text'], group = form.cleaned_data['group'])
                                return redirect('/') 
                form = PostForm()
                return render(request,'new.html',{'form':form})
        return redirect('/') # Если пользователь не авторизован и пытается войти на стр new то его сразу перенаправляет на главную

def profile(request, username):
        author_profile = User.objects.get(username=username)
        posts = Post.objects.filter(author=author_profile).order_by("-pub_date")
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page') 
        page = paginator.get_page(page_number) 
        return render(request, "profile.html", {"posts": posts , "username": username, "author_profile": author_profile, 'page': page, 'paginator': paginator})

def post_view(request, username, post_id):
        author_profile = User.objects.get(username=username)
        post = Post.objects.filter(author=author_profile).get(id=post_id)
        number = Post.objects.filter(author=author_profile).count()
        return render(request, "post.html", {"post": post , "username": username, "author_profile": author_profile, "number": number})

def post_edit(request, username, post_id):
        post = get_object_or_404(Post, id=post_id) 
        if request.user == post.author:
                form = PostForm(request.POST, instance=post)
                if request.method == 'POST':                       
                        if form.is_valid(): 
                                form.save()
                                return redirect('post', username, post_id) 
                form = PostForm(instance=post)               
                return render(request, "new.html", {'form':form, 'post': post})    
        return redirect('post', username, post_id)


        