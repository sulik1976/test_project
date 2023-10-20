from smtplib import SMTPResponseException
import requests
from django.shortcuts import render, redirect
from django.views import View
from .forms import CityForm, AddPostForm
from .models import City, Blog, Category
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse


menu = [
    {'title': "Главная", 'url_name': 'home'},
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Добавить статью", 'url_name': 'add_page'},
    {'title': "Погода в вашем городе", 'url_name': 'weather'},
]

class WeatherView(View):
    template_name = 'blog/weather.html'
    appid = 'e06c8a2f03607612ef71038cc5aa74ba'  # Replace with your valid API key
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + appid

    def get(self, request):
        form = CityForm()
        cities = City.objects.all()
        user_menu = menu.copy()
        user_menu.pop(3)
        all_cities = []
        for city in cities:
            res = requests.get(self.url.format(city.name)).json()
            city_info = {
                'city': city.name,
                'temp': res['main']['temp'],
                'icon': res['weather'][0]['icon']
            }
            all_cities.append(city_info)
        context = {'all_info': all_cities, 'form': form, 'menu': user_menu, 'title': 'Погода в вашем городе'}
        return render(request, self.template_name, context)


    def post(self, request):
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('weather')


def remove_city(request, city_name):
        if request.method == 'POST':
            City.objects.get(name=city_name).delete()
            return redirect('weather')        


def index(request):
    posts = Blog.objects.filter(is_published=True).order_by('-time_create')
    cats = Category.objects.all()
    user_menu = menu.copy()
    user_menu.pop(0)
 
    context = {
        'posts': posts,
        'cats': cats,
        'menu': user_menu,
        'title': 'Главная страница',
        'cat_selected': 0,
        
    }
 
    return render(request, 'blog/index.html', context=context)





def about(request):
    posts = Blog.objects.all()
    cats = Category.objects.all()
    user_menu = menu.copy()
    user_menu.pop(1)
 
    context = {
        'posts': posts,
        'cats': cats,
        'menu': user_menu,
        'title': 'О сайте',
        'cat_selected': 0,
    }
 
    return render(request, 'blog/about.html', context=context)
    

def show_post(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    context = {
        'post': post,
        'menu': menu,
        'title': post.title,
        'cat_selected': 1,
    }
 
    return render(request, 'blog/post.html', context=context)
    

@login_required(login_url='register')
def add_page(request):
    user_menu = menu.copy()
    user_menu.pop(2)
    context = {
    'menu': user_menu,
    'title': 'Добавление статьи',
    }
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddPostForm()
        
    return render(request, 'blog/addpage.html', {**{'form': form}, **context})



def contact(request):
    return SMTPResponseException("Обратная связь")
 

def show_category(request, cat_id):
    posts = Blog.objects.filter(cat_id=cat_id)
    cats = Category.objects.all()
    category = Category.objects.get(id=cat_id)
 
    context = {
        'posts': posts,
        'cats': cats,
        'menu': menu,
        'title': category,
        'cat_selected': cat_id,
    }
 
    return render(request, 'blog/index.html', context=context)    


def register(request):
    if request.method == 'GET':
        return render(request, 'blog/register.html', {'menu': menu, 'title': 'Регистрация', 'form': UserCreationForm(),})
    else:
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






def login_view(request):  # Изменено имя функции
    if request.method == 'GET':
        return render(request, 'blog/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])

        if user is None:
            return render(request, 'blog/login.html',
                          {'form': AuthenticationForm(),
                           'error': 'Неверные данные для входа!'})
        else:
            login(request, user)
            return redirect('home')


def logout_view(request):
    logout(request)
    return redirect('home')                           
