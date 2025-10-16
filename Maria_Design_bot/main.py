from curses.ascii import isdigit
from types import NoneType

import telebot
from telebot import types
import os
import datetime
from pathlib import Path
from config import TOKEN
import json
from typing import cast
import psycopg2
from zoneinfo import ZoneInfo
from psycopg2 import sql
from telebot.handler_backends import State, StatesGroup



bot = telebot.TeleBot(TOKEN)
target_user_id = 178945372
property_type = None
folder_path = None
square = None
project_path = Path(__file__).parent

class UserStates(StatesGroup):
	waiting_contact = State()
	waiting_contact_guide = State()

user_data = {}
contact_state = {}
class User:

	def __init__(self, first_name):
		self.user_id = 0
		self.first_name = first_name
		self.user_name = ''
		self.square = float
		self.date = datetime.datetime

def load_dbconfig(config_file='dbconfig.json'):
	with open(config_file) as f:
		return json.load(f)

config = load_dbconfig()
db_config = config['database']

def check_db_connection():
	try:
		conn = psycopg2.connect(
			dbname=db_config['dbname'],
			user=db_config['user'],
			password=db_config['password'],
			host=db_config['host'],
			port=db_config['port']
		)
		conn.close()
		return True
	except Exception as e:
		print(f"Ошибка подключения к базе данных: {e}")
		return False

# cursor = conn.cursor
# cursor.execute(f'CREATE TABLE users (user_id INT,'
# 			   						f'first_name varchar(100),'
# 			   						f'user_name varchar(100),'
# 									f'square float,'
# 									f'datetime datetime)'
# 			   )

def insert_user_data(message, reason):
	conn = psycopg2.connect(
		dbname=db_config['dbname'],
		user=db_config['user'],
		password=db_config['password'],
		host=db_config['host'],
		port=db_config['port']
	)
	cursor = conn.cursor()
	user_data[message.from_user.id].user_name = message.from_user.username
	user_data[message.from_user.id].square = square
	user_data[message.from_user.id].date = datetime.datetime.now()
	user_iter = iter(user_data.keys())
	user_id = next(user_iter)
	user = user_data[user_id]
	user_id = message.from_user.id
	sql = 'INSERT INTO dbo.users (user_id, first_name, user_name, square, datetime, reason) VALUES (%s, %s, %s, %s ,%s, %s)'
	val = (user_id, user.first_name, user.user_name, user.square, user.date, reason)
	cursor.execute(sql, val)
	conn.commit()
	user_data.clear()

def format_table(column_names, rows):
	# Форматируем таблицу
	table = ""

	# Добавляем шапку
	table += " | ".join(column_names) + "\n"
	table += "-" * (len(column_names) * 18) + "\n"  # Разделитель на основе длины шапки

	# Добавляем строки данных
	for row in rows:
		table += " | ".join(map(str, row)) + "\n"
	return table

def send_table(chat_id, table):
	bot.send_message(chat_id, f"<pre>{table}</pre>", parse_mode='HTML')

def start_message(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	info_btn = types.KeyboardButton('🖌️ О студии')
	markup.row(info_btn)
	calc_btn = types.KeyboardButton('💸 Индивидуальный рассчет')
	descr_btn = types.KeyboardButton('📋 Описание услуг')
	markup.row(calc_btn, descr_btn)
	guide_btn = types.KeyboardButton('🧭 Гайд по ремонту')
	markup.row(guide_btn)
	main_photo = Path(f'{project_path}/Main_photo/Maria_main_photo.jpg')
	with open ('Text/Greeting.txt', 'r', encoding='utf-8') as file:
		lines = file.readlines()
	first_message = f'Привет {message.from_user.first_name}!\n\n' + ''.join(lines)
	bot.send_photo(message.chat.id, photo=open(main_photo, 'rb'), caption=first_message,
				   reply_markup=markup)

def menu_message(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	info_btn = types.KeyboardButton('🖌️ О студии')
	markup.row(info_btn)
	calc_btn = types.KeyboardButton('💸 Индивидуальный рассчет')
	descr_btn = types.KeyboardButton('📋 Описание услуг')
	markup.row(calc_btn, descr_btn)
	guide_btn = types.KeyboardButton('🧭 Гайд по ремонту')
	markup.row(guide_btn)
	bot.send_message(message.chat.id, 'Главное меню',
	 					 reply_markup=markup)

def menu_message_from_guide(message):
	user_data[message.from_user.id] = User(message.from_user.first_name)
	insert_reason = 'Скачали гайд, без контакта'
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	info_btn = types.KeyboardButton('🖌️ О студии')
	markup.row(info_btn)
	calc_btn = types.KeyboardButton('💸 Индивидуальный рассчет')
	descr_btn = types.KeyboardButton('📋 Описание услуг')
	markup.row(calc_btn, descr_btn)
	guide_btn = types.KeyboardButton('🧭 Гайд по ремонту')
	markup.row(guide_btn)
	bot.send_message(message.chat.id, f'Благодарим Вас, отправляем файл-гайд по ремонту с полезными ссылками внутри🤗',
	 					 reply_markup=markup)
	guide_file = Path(f'{project_path}/Files/Гайд по ремонту.pdf')
	bot.send_document(message.chat.id, document=open(guide_file, 'rb'))
	insert_user_data(message, insert_reason)


@bot.message_handler(commands=['start'])
def handle_start(message):
	start_message(message)

def ask_for_contact(message):
	# Создаем кнопку для запроса контакта
	keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	button_contact = types.KeyboardButton(text="💬 Поделиться контактом", request_contact=True)
	button_menu = types.KeyboardButton(text="🏠 Вернуться в меню")
	keyboard.add(button_contact,button_menu)
	message_text = (f'Если вас заинтересовало предложение,\n'
					f'поделитесь контактом и мы свяжемся с вами')
	# Отправляем сообщение с кнопкой
	if isinstance(message,types.Message):
		bot.send_message(message.chat.id, message_text
						 ,reply_markup=keyboard)
	elif isinstance(message,types.CallbackQuery):
		bot.send_message(message.message.chat.id, message_text
						 ,reply_markup=keyboard)
	bot.set_state(message.from_user.id, UserStates.waiting_contact, message.chat.id)

def ask_for_contact_guide(message):
	# Создаем кнопку для запроса контакта
	keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	button_contact = types.KeyboardButton(text="💬 Поделиться контактом и получить гайд", request_contact=True)
	button_menu = types.KeyboardButton(text="🏠 Вернуться в меню и получить гайд")
	keyboard.add(button_contact,button_menu)
	message_text = (f'Чтобы получить гайд с промокодами на скидки, поделитесь, пожалуйста, вашими контактыми данными.\n\n'
					f'Предоставляя контакты вы даете согласие на обработку своих персональных данных')
	# Отправляем сообщение с кнопкой
	if isinstance(message,types.Message):
		bot.send_message(message.chat.id, message_text
						 ,reply_markup=keyboard)
	elif isinstance(message,types.CallbackQuery):
		bot.send_message(message.message.chat.id, message_text
						 ,reply_markup=keyboard)
	bot.set_state(message.from_user.id, UserStates.waiting_contact_guide, message.chat.id)

def insert_contact(message,reason):
	# Установка часового пояса Екатеринбурга (UTC+5)
	tz_ekb = ZoneInfo('Asia/Yekaterinburg')
	date = datetime.datetime.now(tz_ekb)
	conn = psycopg2.connect(
		dbname=db_config['dbname'],
		user=db_config['user'],
		password=db_config['password'],
		host=db_config['host'],
		port=db_config['port']
		)
	cursor = conn.cursor()
	contact = message.contact
	phone_number = contact.phone_number
	first_name = contact.first_name
	last_name = contact.last_name if contact.last_name else ""
	date = datetime.datetime.now()
	sql_query = f"INSERT INTO dbo.users (phone_number, first_name, last_name, datetime, reason) VALUES (%s, %s, %s, %s, %s)"
	val = (phone_number, first_name, last_name, date, reason)
	cursor.execute(sql_query, val)
	conn.commit()


	# print(f'{phone_number},{type(phone_number)}')
	# except Exception as e:
	# 	pass

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			current_state = bot.get_state(message.from_user.id, message.chat.id)
		if current_state == UserStates.waiting_contact.name:
			while message.contact is not None:
				try:
					reason_insert = 'Просьба связаться'
					insert_contact(message, reason_insert)
					bot.send_message(message.chat.id, f'Спасибо, мы свяжемся с Вами в ближайшее время🤗')
					menu_message(message)
					message.contact = None
					break
				except Exception as e:
					pass

		elif current_state == UserStates.waiting_contact_guide.name:
			while message.contact is not None:
				try:
					reason_insert = 'Скачали гайд, оставили контакт'
					insert_contact(message, reason_insert)
					bot.send_message(message.chat.id, f'Благодарим Вас, отправляем файл-гайд по ремонту с полезными ссылками внутри🤗')
					guide_file = Path(f'{project_path}/Files/Гайд по ремонту.pdf')
					bot.send_document(message.chat.id, document=open(guide_file, 'rb'))
					menu_message(message)
					message.contact = None
					bot.delete_state(message.from_user.id, message.chat.id)
					break
				except Exception as e:
					pass

@bot.message_handler(content_types=['text'])
def on_click(message):
	if message.text.lower() == '📋 описание услуг':
		service_description(message)
	elif message.text.lower() == '🖌️ о студии':
		studio_info(message)
	elif message.text.lower() == '💸 индивидуальный рассчет':
		personal_calc(message)
	elif message.text.lower() == '🏠 вернуться в меню':
		menu_message(message)
	elif message.text.lower() == '🏠 вернуться в меню и получить гайд':
		menu_message_from_guide(message)
	elif message.text.lower() == '🧭 гайд по ремонту':
		ask_for_contact_guide(message)



def service_description(message):
	descr_photo_dir = Path(f'{project_path}/description_photo')
	for file in os.listdir(descr_photo_dir):
		with open(os.path.join(descr_photo_dir, file), 'rb') as photo:
			bot.send_photo(message.chat.id,photo)

def studio_info(message):
	markup_info = types.InlineKeyboardMarkup()
	pictures = types.InlineKeyboardButton(text = f'🖼️ Интерьерные картины'
														,callback_data='info_Интерьерные картины')
	about = types.InlineKeyboardButton('💁 Обо мне', callback_data='info_Обо мне')
	contacts = types.InlineKeyboardButton('📞 Контакты', callback_data='info_Контакты')
	portfolio = types.InlineKeyboardButton('📂 Портфолио проектов', callback_data='info_Портфолио')
	markup_info.row(about, contacts)
	markup_info.row(pictures)
	markup_info.row(portfolio)
	bot.send_message(message.chat.id, f'Давайте познакомимся поближе 🤗',
					 reply_markup=markup_info)

@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def info(call):
	if call.data == 'info_Интерьерные картины':
		global folder_path
		folder_path = Path(f'{project_path}/Portfolio/Pictures')
		pictures = []
		for filename in os.listdir(folder_path):
			if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):  # фильтруем только изображения
				file_path = os.path.join(folder_path, filename)
				photo_file = cast(str, file_path)
				pictures.append(telebot.types.InputMediaPhoto(open(photo_file, 'rb')))
		with open('Text/pictures.txt', 'r', encoding='utf-8') as file:
			lines = file.readlines()
		picture_message = ''.join(lines)
		bot.send_message(call.from_user.id, picture_message)
		bot.send_media_group(call.message.chat.id, pictures)
		ask_for_contact(call.message)
		handle_contact(call.message)

		# bot.register_next_step_handler(call.message, menu_message)
	elif call.data == 'info_Обо мне':
		with open('Text/about_me.txt', 'r', encoding='utf-8') as file:
			lines = file.readlines()
		contacts_info = ''.join(lines)
		bot.send_message(call.from_user.id, contacts_info)
	elif call.data == 'info_Контакты':
		with open('Text/contacts.txt', 'r', encoding='utf-8') as file:
			lines = file.readlines()
		contacts_info = f'Контактная информация\n\n' + ''.join(lines)
		bot.send_message(call.from_user.id, contacts_info)
	elif call.data == 'info_Портфолио':
		portfolio(call)

@bot.callback_query_handler(func=lambda call: call.data == 'info_Портфолио')
def portfolio(call):
	markup = types.InlineKeyboardMarkup()
	bedroom = types.InlineKeyboardButton('🛏️️ Спальни', callback_data='portfolio_Спальни')
	living_room = types.InlineKeyboardButton('🛋️ Кухни-гостиные', callback_data='portfolio_Кухни-гостиные')
	child_room = types.InlineKeyboardButton('🤸 Детские', callback_data='portfolio_Детские')
	bathroom = types.InlineKeyboardButton('🛁 Ванные комнаты и санузлы', callback_data='portfolio_Ванные комнаты и санузлы')
	markup.row(bedroom,living_room)
	markup.row(child_room)
	markup.row(bathroom)
	bot.send_message(call.message.chat.id, f'Пожалуйста, выберите тип помещения для просмотра',
					 reply_markup=markup)

@bot.callback_query_handler(func=lambda call:call.data.startswith('portfolio_'))
def callback_portfolio(call):
	global folder_path
	folder_path = project_path  # Укажите путь к вашей папке с изображениями
	media = []

	if call.data[10:] == 'Спальни':
		folder_path = Path(f'{project_path}/Portfolio/BedRoom')
	elif call.data[10:] == 'Кухни-гостиные':
		folder_path = Path(f'{project_path}/Portfolio/LivingRoom')
	elif call.data[10:] == 'Ванные комнаты и санузлы':
		folder_path = Path(f'{project_path}/Portfolio/BathRoom')
	elif call.data[10:] == 'Детские':
		folder_path = Path(f'{project_path}/Portfolio/ChildrenRoom')
	# Проходим по всем файлам в папке
	for filename in os.listdir(folder_path):
		if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):  # фильтруем только изображения
			file_path = os.path.join(folder_path, filename)
			photo_file = cast(str,file_path)
			media.append(telebot.types.InputMediaPhoto(open(photo_file, 'rb')))
	if media:
		bot.send_message(call.message.chat.id, f'Портфолио - {call.data[10:]}')
		bot.send_media_group(call.message.chat.id, media)
	else:
		bot.send_message(call.message.chat.id, "Нет изображений для отправки.")

def personal_calc(message):
	markup = types.InlineKeyboardMarkup()
	full_project = types.InlineKeyboardButton('🗝️ Под ключ',callback_data='project_Дизайн-проект под ключ')
	project = types.InlineKeyboardButton('💥Дизайн-проект', callback_data='project_Дизайн-проект')
	express = types.InlineKeyboardButton('🚅 Экспресс', callback_data='project_Экспресс проект')
	project_about = types.InlineKeyboardButton('Подробнее чем отличаются услуги', callback_data='project_about_services')
	markup.row(full_project)
	markup.row(project,express)
	markup.row(project_about)
	bot.send_message(message.chat.id, f'Пожалуйста, выберите тип услуги',
					 reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('project_'))
def callback_property_type(call):
	global property_type
	property_type = call.data[8:]
	if property_type == 'about_services':
		service_description(call.message)
		personal_calc(call.message)
	else:
		bot.send_message(call.from_user.id, f'Вы выбрали: {property_type}')
		square_input(call.message)

def square_input(message):
	bot.send_message(message.chat.id,'Введите площадь помещения:')
	bot.register_next_step_handler(message, write_square)

def write_square(message):
	user_data[message.from_user.id] = User(message.from_user.first_name)
	while True:
		global square
		square = message.text
		price = float()
		if property_type == 'Дизайн-проект под ключ':
			price = 3000
		elif (property_type == 'Дизайн-проект') or (property_type == 'express_project' and float(square) <=5):
			price = 2500
		elif property_type == 'Экспресс проект' and float(square) >5:
			price = 2200
		try:
			insert_reason = 'Индивидуальный расчет'
			calc = float(square) * price
			calc_result = '{0:,}'.format(calc).replace(',', ' ')
			period = int(0)
			if 0 <= float(square) <= 15:
				period = 14
			elif float(square) > 15:
				period = float(square) * 1
			with open(f'Text/{property_type}.txt', 'r', encoding='utf-8') as file:
				lines = file.readlines()
			message_calc = (
						f'{property_type}\n\n'
						f'{"".join(lines)}\n'
					    f'💸 Общая стоимость услуг - {str(calc_result)} рублей\n'
					    f'📅 Срок выполнения - {int(period)} рабочих дней')
			bot.send_message(message.chat.id, message_calc)
			insert_user_data(message,insert_reason)
			ask_for_contact(message)
			handle_contact(message)
			# message.contact = None
			# bot.register_next_step_handler(message, menu_message)
			# bot.register_next_step_handler(message, menu_message)
			break
		except ValueError:
			bot.send_message(message.chat.id,'Неверный формат значения площади, введите число')
			personal_calc(message)
			break
bot.infinity_polling()