import os

import telebot
from dotenv import load_dotenv
from telebot import types
import requests
import pytz
from datetime import datetime

load_dotenv()
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
current_city = ""


@bot.message_handler(content_types=['text'])
def get_weather(message):
    global current_city
    current_city = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_temperature = types.InlineKeyboardButton("Температура", callback_data='temperature')
    item_wind_speed = types.InlineKeyboardButton("Скорость ветра", callback_data='wind_speed')
    item_sunrise_sunset = types.InlineKeyboardButton("Восход и закат", callback_data='sunrise_sunset')
    markup.add(item_temperature, item_wind_speed, item_sunrise_sunset)

    bot.send_message(message.chat.id, "Выберите, что вы хотите узнать о погоде:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    city = current_city
    try:
        if call.data == 'temperature':

            url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
            weather_data = requests.get(url).json()
            if 'weather' not in weather_data:
                bot.send_message(call.message.chat.id, "Город не найден. Проверьте правильность ввода города, либо смените язык ввода.")
                return
            weather = weather_data['weather'][0]['description']
            temperature = round(weather_data['main']['temp'])
            temperature_feels = round(weather_data['main']['feels_like'])
            text = f'Сейчас в городе {city} {temperature} °C. ' \
                   f'Ощущается как {temperature_feels}°C.' \
                   f' {weather}.'

            bot.send_message(call.message.chat.id, text)
        elif call.data == 'wind_speed':
            url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
            weather_data = requests.get(url).json()
            wind_speed = round(weather_data['wind']['speed'])
            text = f'Скорость ветра {wind_speed} м/с.'

            bot.send_message(call.message.chat.id, text)
        elif call.data == 'sunrise_sunset':
            url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
            weather_data = requests.get(url).json()

            sunrise_unix = weather_data.get('sys', {}).get('sunrise', 0)
            sunset_unix = weather_data.get('sys', {}).get('sunset', 0)
            city_timezone = pytz.timezone(pytz.country_timezones.get(weather_data.get('sys', {}).get('country', 'US'))[0])
            sunrise_local = datetime.fromtimestamp(sunrise_unix, tz=pytz.utc).astimezone(city_timezone).time()
            sunset_local = datetime.fromtimestamp(sunset_unix, tz=pytz.utc).astimezone(city_timezone).time()

            sunrise_sunset = f'Восход солнца: {sunrise_local}\nЗакат солнца: {sunset_local}'

            bot.send_message(call.message.chat.id, sunrise_sunset)
    except KeyError:
        bot.send_message(call.message.chat.id,
                         "Город не найден. Проверьте правильность ввода города, либо смените язык ввода.")


bot.polling()
