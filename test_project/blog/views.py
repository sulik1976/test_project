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
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from smtplib import SMTPResponseException
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import requests



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
            try:
                res = requests.get(self.url.format(city.name)).json()
                if 'main' in res:
                    city_info = {
                        'city': city.name,
                        'temp': res['main']['temp'],
                        'icon': res['weather'][0]['icon']
                    }
                    all_cities.append(city_info)
                else:
                    all_cities.append({
                        'city': city.name,
                        'error': 'Ошибка: такого города нет'
                    })
            except ObjectDoesNotExist:
                
                pass
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


class IndexView(ListView):
    model = Blog
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-time_create']


    def get_queryset(self):
        return Blog.objects.filter(is_published=True).order_by('-time_create')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cats'] = Category.objects.all()
        context['menu'] = menu.copy()
        context['menu'].pop(0)
        context['title'] = 'Главная страница'
        context['cat_selected'] = 0
        return context


class AboutView(TemplateView):
    template_name = 'blog/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Blog.objects.all()
        context['cats'] = Category.objects.all()
        context['menu'] = menu.copy()
        context['menu'].pop(1)
        context['title'] = 'О сайте'
        context['cat_selected'] = 0
        return context


class ShowPostView(View):
    def get(self, request, post_slug):
        post = get_object_or_404(Blog, slug=post_slug)
        context = {
            'post': post,
            'menu': menu,
            'title': post.title,
            'cat_selected': 1,
        }

        return render(request, 'blog/post.html', context=context)


@method_decorator(login_required(login_url='register'), name='dispatch')
class AddPageView(View):
    def get(self, request):
        user_menu = menu.copy()
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
            user_menu = menu.copy()
            user_menu.pop(2)
            context = {
                'menu': user_menu,
                'title': 'Добавление статьи',
            }
            return render(request, 'blog/addpage.html', {**{'form': form}, **context})
 

class ShowCategoryView(View):
    def get(self, request, cat_id):
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


class RegisterView(View):
    def get(self, request):
        return render(request, 'blog/register.html', {'menu': menu, 'title': 'Регистрация', 'form': UserCreationForm(),})

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
        return render(request, 'blog/login.html', {'form': AuthenticationForm()})

    def post(self, request):
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])

        if user is None:
            return render(request, 'blog/login.html',
                          {'form': AuthenticationForm(),
                           'error': 'Неверные данные для входа!'})
        else:
            login(request, user)
            return redirect('home')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
