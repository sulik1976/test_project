from django.urls import path
from . import views 
from .views import *


urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('weather/', WeatherView.as_view(), name='weather'),
    path('post/<str:post_slug>/', views.ShowPostView.as_view(), name='post'),
    path('addpage/', views.AddPageView.as_view(), name='add_page'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('category/<int:cat_id>/', views.ShowCategoryView.as_view(),name='category'),
    path('remove_city/<str:city_name>/', RemoveCityView.as_view(), name='remove_city'),
]