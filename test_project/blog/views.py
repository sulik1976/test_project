from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from .forms import CityForm, AddPostForm
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from .models import City, Blog, Category
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseRedirect, JsonResponse
# from django.core.exceptions import ObjectDoesNotExist
# from smtplib import SMTPResponseException
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Comment
from .forms import CommentForm
# from django.http import HttpResponseForbidden
from .utils import get_user_context, get_weather_data
from .utils import *
import requests


class WeatherView(View):
    template_name = 'blog/weather.html'
    appid = 'e06c8a2f03607612ef71038cc5aa74ba' 

    def get(self, request):
        form = CityForm()
        cities = City.objects.all()
        user_menu = get_user_context()['menu']
        user_menu.pop(3)
        all_cities = get_weather_data(cities, self.appid)
        context = {'all_info': all_cities, 'form': form, 'menu': user_menu, 'title': 'Погода в вашем городе'}
        return render(request, self.template_name, context)

    def post(self, request):
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('weather')

class RemoveCityView(View):
    def post(self, request, *args, **kwargs):
        city_name = kwargs.get('city_name')
        City.objects.filter(name=city_name).delete()
        return redirect('weather')


class IndexView(DataMixin, ListView):
    model = Blog
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-time_create']
    

    def get_queryset(self):
        return Blog.objects.filter(is_published=True).order_by('-time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cats'] = Category.objects.all()
        user_menu = get_user_context()['menu']
        user_menu.pop(0)
        context['menu'] = user_menu
        context['title'] = 'Главная страница'
        context['cat_selected'] = 0
        return context

class AboutView(TemplateView):
    template_name = 'blog/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Blog.objects.all()
        context['cats'] = Category.objects.all()
        user_menu = get_user_context()['menu']
        user_menu.pop(1)
        context['menu'] = user_menu
        context['title'] = 'О сайте'
        context['cat_selected'] = 0
        return context

class ShowPostView(View):
    def get(self, request, post_slug):
        post = get_object_or_404(Blog, slug=post_slug)
        comments = Comment.objects.filter(post=post)
        form = CommentForm()
        context = {
            'post': post,
            'comments': comments,
            'form': form,
            'menu': get_user_context()['menu'],
            'title': post.title,
            'cat_selected': 1,
        }
        return render(request, 'blog/post.html', context=context)

    def post(self, request, post_slug):
        post = get_object_or_404(Blog, slug=post_slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                comment = form.save(commit=False)
                comment.user = request.user
                comment.post = post
                comment.save()
            else:
                return redirect('register')     
        return redirect('post', post_slug=post_slug)


@method_decorator(login_required(login_url='register'), name='dispatch')
class AddPageView(View):
    def get(self, request):
        user_menu = get_user_context()['menu']
        user_menu.pop(2)
        context = {
            'menu': user_menu,
            'title': 'Добавление статьи',
        }
        form = AddPostForm()
        return render(request, 'blog/addpage.html', {**{'form': form}, **context})

    def post(self, request):
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            user_menu = get_user_context()['menu']
            user_menu.pop(2)
            context = {
                'menu': user_menu,
                'title': 'Добавление статьи',
            }
            return render(request, 'blog/addpage.html', {**{'form': form}, **context})        


class ShowCategoryView(DataMixin, View):
    def get(self, request, cat_id):
        category = get_object_or_404(Category, id=cat_id)
        posts = Blog.objects.filter(cat_id=cat_id, is_published=True)
        cats = Category.objects.all()
        context = {
            'cats': cats,
            'posts': posts,
            'menu': get_user_context()['menu'],
            'title': category.name,
            'cat_selected': 1,
        }
        return render(request, 'blog/index.html', context=context)   



class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        context = {
            'form': form,
            'menu': get_user_context()['menu'],
            'title': 'Регистрация',
            'cat_selected': 0,
        }
        return render(request, 'blog/register.html', context=context)

    def post(self, request):
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'blog/register.html',
                              {'form': UserCreationForm(),
                               'error': 'Такое имя пользователя уже существует! Попробуйте другое'})
        else:
            return render(request, 'blog/register.html',
                          {'form': UserCreationForm(),
                           'error': 'Пароли не совпали!'})



class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        context = {
            'form': form,
            'menu': get_user_context()['menu'],
            'title': 'Вход',
            'cat_selected': 0,
        }
        return render(request, 'blog/login.html', context=context)

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            context = {
                'form': form,
                'menu': get_user_context()['menu'],
                'title': 'Вход',
                'cat_selected': 0,
            }
            return render(request, 'blog/login.html', context=context)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
