from .models import *
import requests

def get_user_context():
    return {
        'menu': [
            {'title': "Главная", 'url_name': 'home'},
            {'title': "О сайте", 'url_name': 'about'},
            {'title': "Добавить статью", 'url_name': 'add_page'},
            {'title': "Погода в вашем городе", 'url_name': 'weather'},
        ]
    }

def get_weather_data(cities, appid):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&appid=' + appid
    all_cities = []
    for city in cities:
        try:
            res = requests.get(url.format(city.name)).json()
            if 'main' in res:
                city_info = {
                    'city': city.name,
                    'temp': res['main']['temp'],
                    'icon': res['weather'][0]['icon'],
                    'description': res['weather'][0]['description'],
                    'humidity': res['main']['humidity'],
                    'pressure': res['main']['pressure'],
                    'wind_speed': res['wind']['speed']
                }
                all_cities.append(city_info)
            else:
                all_cities.append({
                    'city': city.name,
                    'error': 'Ошибка: такого города нет'
                })
        except ObjectDoesNotExist:
            pass
    return all_cities

class DataMixin:    
    paginate_by = 3
