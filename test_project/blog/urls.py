from django.urls import path
from .views import WeatherView
from . import views 
from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('about/', about, name='about'),
    path('weather/', WeatherView.as_view(), name='weather'),
    path('post/<slug:post_slug>/', show_post, name='post'),
    path('addpage/', add_page, name='add_page'),
    path('contact/', contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('category/<int:cat_id>/', show_category, name='category'),
    path('remove_city/<str:city_name>/', views.remove_city, name='remove_city'),
]