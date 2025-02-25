from curses.ascii import isdigit
import telebot
from telebot import types
import os
from pathlib import Path
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
property_type = None
project_path = Path(__file__).parent

@bot.message_handler(commands=['start'])
def start_message(message):
	markup = types.ReplyKeyboardMarkup()
	info_btn = types.KeyboardButton('О студии')
	markup.row(info_btn)
	calc_btn = types.KeyboardButton('Индивидуальный рассчет')
	descr_btn = types.KeyboardButton('Описание услуг')
	markup.row(calc_btn, descr_btn)
	main_photo = Path(f'{project_path}/Main_photo/Maria_main_photo.jpg')
	with open ('Text/Greeting.txt', 'r', encoding='utf-8') as file:
		lines = file.readlines()
	first_message = f'Привет {message.from_user.first_name}!\n\n' + ''.join(lines)
	bot.send_photo(message.chat.id, photo=open(main_photo, 'rb'), caption=first_message,
				   reply_markup=markup)

@bot.message_handler(content_types=['text'])
def on_click(message):
	if message.text.lower() == 'описание услуг':
		service_description(message)
		# bot.send_message(message.chat.id, 'Описание услуг')
	elif message.text.lower() == 'о студии':
		studio_info(message)
		# bot.register_next_step_handler(message, studio_info)
	elif message.text.lower() == 'индивидуальный рассчет':
		personal_calc(message)
		# bot.register_next_step_handler(message, personal_calc)


def service_description(message):
	# project_path = Path(__file__).parent
	descr_photo_dir = Path(f'{project_path}/description_photo')
	for file in os.listdir(descr_photo_dir):
		with open(os.path.join(descr_photo_dir, file), 'rb') as photo:
			bot.send_photo(message.chat.id,photo)

def studio_info(message):
	markup_info = types.InlineKeyboardMarkup()
	pictures = types.InlineKeyboardButton(text = f'Картины'
														,callback_data='info_Интерьерные картины')
	about = types.InlineKeyboardButton('Обо мне', callback_data='info_Обо мне')
	contacts = types.InlineKeyboardButton('Контакты', callback_data='info_Контакты')
	markup_info.add(about, contacts,pictures)
	bot.send_message(message.chat.id, f'Познакомимся по-ближе',
					 reply_markup=markup_info)

@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def info(call):
	if call.data == 'info_Интерьерные картины':
		bot.send_message(call.from_user.id, f'Здесь будет инфо про картины')
	elif call.data == 'info_Обо мне':
		bot.send_message(call.from_user.id, f'Здесь будет информация Обо мне')
	elif call.data == 'info_Контакты':
		bot.send_message(call.from_user.id, f'Здесь будет контактная информация')


def personal_calc(message):
	# bot.send_message(message.chat.id, 'Пожалуйста, выберите услуги')
	markup = types.InlineKeyboardMarkup()
	full_project = types.InlineKeyboardButton('Под ключ',callback_data='Дизайн-проект под ключ')
	project = types.InlineKeyboardButton('Дизайн-проект', callback_data='Дизайн-проект')
	express = types.InlineKeyboardButton('Экспресс', callback_data='Экспресс проект')
	project_about = types.InlineKeyboardButton('Подробнее чем отличаются услуги', callback_data='about_services')
	markup.add(full_project, project,express, project_about)
	bot.send_message(message.chat.id, f'Пожалуйста, выберите тип услуги',
					 reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def callback_property_type(call):
	global property_type
	property_type = call.data
	if property_type == 'about_services':
		service_description(call.message)
		personal_calc(call.message)
	else:
		bot.send_message(call.from_user.id, f'Вы выбрали: {property_type}')
		# bot.register_next_step_handler(call.message, square_input)
		square_input(call.message)

def square_input(message):
	bot.send_message(message.chat.id,'Введите площадь помещения:')
	bot.register_next_step_handler(message, write_square)

def write_square(message):
	while True:
		square = message.text
		price = float()
		if property_type == 'Дизайн-проект под ключ':
			price = 2500
		elif (property_type == 'Дизайн-проект') or (property_type == 'express_project' and float(square) <=5):
			price = 2000
		elif property_type == 'Экспресс проект' and float(square) >5:
			price = 1800
		try:
			calc = float(square) * price
			period = int(0)
			if 0 <= float(square) <= 15:
				period = 14
			elif float(square) > 15:
				period = float(square) * 1
			bot.send_message(message.chat.id, f'{str(calc)} рублей\n'
							 					   f'{int(period)} рабочих дней на выполнение проекта')
			break
		except ValueError:
			bot.send_message(message.chat.id,'Введите число, неверный формат значения площади')
			personal_calc(message)
			break
bot.infinity_polling()