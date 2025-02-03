import telebot
from telebot import types
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
	markup = types.ReplyKeyboardMarkup()
	info_btn = types.KeyboardButton('О студии')
	markup.row(info_btn)
	calc_btn = types.KeyboardButton('Индивидуальный рассчет')
	descr_btn = types.KeyboardButton('Описание услуг')
	markup.row(calc_btn, descr_btn)
	bot.send_photo(message.chat.id, photo=open('D:/Python/TG_bots/Maria_Design_bot/Maria_photo.jpg', 'rb'))
	bot.send_message(message.chat.id,f'Привет {message.from_user.first_name}!\n'
									 	  f'Меня зовут Мария Бондаренкова\n'
									 	  f'я - дизайнер интерьеров',
											reply_markup=markup)
	bot.register_next_step_handler(message, on_click)

def on_click(message):
	if message.text == 'Описание услуг':
		bot.send_message(message.chat.id,'тут фото')
		# bot.register_next_step_handler(message, service_description)
	elif message.text == 'Индивидуальный рассчет':
		bot.register_next_step_handler(message, personal_calc)
	elif message.text == 'О студии':
		bot.register_next_step_handler(message, studio_info)

def service_description(message):
	photo_dir = 'D:/Python/TG_bots/Maria_Design_bot/description_photo'

	# for file in os.listdir(photo_dir):
	# 	with open(os.path.join(photo_dir, file), 'r', encoding='utf-8') as photo:
	# 		print(photo)

bot.infinity_polling()