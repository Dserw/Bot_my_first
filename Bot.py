import telebot
from config import keys, TOKEN
from extensions import CriptoConverter, ConvertionException
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_help(message: telebot.types.Message):
    text = 'Чтобы начать работу введите команду боту в формате:' \
'<имя валюты, цену которой хотите узнать>' \
' <имя валюты, в которую нужно перевести>' \
' <количество переводимой валюты>\nПосмотреть доступные валюты: /values'
    bot.reply_to(message, text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты!'
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        value = message.text.split(' ')

        if len(value) != 3:
            raise ConvertionException('Много параметров.')

        quote, base, amount = value
        total_base = CriptoConverter.get_price(quote, base, amount)
    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Неудалось обработать команду\n{e}')
    else:
        total_base = float(total_base) * float(amount)
        text = f'Цена {amount} {quote} в {base} - {total_base}'
        bot.send_message(message.chat.id, text)

bot.polling()
