from curses.ascii import isdigit

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
	# bot.send_photo(message.chat.id, photo=open('D:/Python/TG_bots/Maria_Design_bot/Maria_photo.jpg', 'rb'))
	bot.send_message(message.chat.id,f'Привет {message.from_user.first_name}!\n'
									 	  f'Меня зовут Мария Бондаренкова\n'
									 	  f'я - дизайнер интерьеров',
											reply_markup=markup)
	# bot.register_next_step_handler(message, on_click)

@bot.message_handler(content_types=['text'])
def on_click(message):
	if message.text.lower() == 'описание услуг':
		service_description(message)
		# bot.send_message(message.chat.id, 'Описание услуг')
	elif message.text.lower() == 'о студии':
		bot.register_next_step_handler(message, studio_info)
	elif message.text == 'Индивидуальный рассчет':
		bot.register_next_step_handler(message, personal_calc)


def service_description(message):
	# bot.send_message(message.chat.id,'Описание услуг')
	photo_dir = 'D:/Python/TG_bots/Maria_Design_bot/description_photo'
	for file in os.listdir(photo_dir):
		with open(os.path.join(photo_dir, file), 'rb') as photo:
			bot.send_photo(message.chat.id,photo)

def studio_info(message):
	bot.send_message(message.chat.id, f'Уважаемый {message.from_user.first_name}!\n'
									  f'здесь представлена информация\n'
									  f'о студии'
					 )

def personal_calc(message):
	bot.send_message(message.chat.id,'Введите площадь помещения:')
	bot.register_next_step_handler(message, write_square)

def write_square(message):
	while True:
		square = float(message.text)
		try:
			calc = float(square)*2500
			period = int(0)
			if 0 <= square <= 15:
				period = 10
			elif 16 <= square <= 50:
				period = 20
			elif square > 50:
				period = square * 0.5
			bot.send_message(message.chat.id, f'{str(calc)} рублей\n'
							 					   f'{int(period)} рабочих дней на выполнение проекта')

			break
		except ValueError:
			bot.send_message(message.chat.id,'Введите число, неверный формат значения площади')
			personal_calc(message)
			break
bot.infinity_polling()