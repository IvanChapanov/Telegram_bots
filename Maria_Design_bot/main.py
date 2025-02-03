import telebot
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_photo(message.chat.id, photo=open('D:/Python/TG_bots/Maria_Design_bot/Maria_photo.jpg', 'rb'))
	bot.send_message(message.chat.id,f'Привет')


bot.infinity_polling()