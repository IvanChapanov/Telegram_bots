from curses.ascii import isdigit
import telebot
from telebot import types
import os
import sys
import datetime
from pathlib import Path
import mysql.connector
from mysql.connector import errorcode
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
property_type = None
square = None
project_path = Path(__file__).parent

user_data = {}

class User:

	def __init__(self, first_name):
		self.user_id = 0
		self.first_name = first_name
		self.user_name = ''
		self.square = float
		self.date = datetime.datetime

try:
	db = mysql.connector.connect(
      host='localhost',
      user='root',
      passwd='Mgc3461422939.',
      port='3306',
      database='dbo'
    )
except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
		sys.exit()
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
		sys.exit()
	else:
		print(err)
		sys.exit()

cursor = db.cursor()
# cursor.execute(f'CREATE TABLE users (user_id INT,'
# 			   						f'first_name varchar(100),'
# 			   						f'user_name varchar(100),'
# 									f'square float,'
# 									f'datetime datetime)'
# 			   )

def fetch_data_from_db(message):

	user_data[message.from_user.id].user_name = message.from_user.username
	user_data[message.from_user.id].square = square
	user_data[message.from_user.id].date = datetime.datetime.now()
	user_iter = iter(user_data.keys())
	user_id = next(user_iter)
	user = user_data[user_id]
	sql = 'INSERT INTO users (user_id, first_name, user_name, square, datetime) VALUES (%s, %s, %s, %s ,%s)'
	val = (user_id, user.first_name, user.user_name, user.square, user.date)
	cursor.execute(sql, val)
	db.commit()
	user_data.clear()
	cursor.execute('SELECT * FROM v_users_request')
	rows = cursor.fetchall()
	column_names = [i[0] for i in cursor.description]
	cursor.close()
	return column_names, rows


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


@bot.message_handler(commands=['start'])
def start_message(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	info_btn = types.KeyboardButton('🖌️ О студии')
	markup.row(info_btn)
	calc_btn = types.KeyboardButton('💸 Индивидуальный рассчет')
	descr_btn = types.KeyboardButton('📋 Описание услуг')
	markup.row(calc_btn, descr_btn)
	main_photo = Path(f'{project_path}/Main_photo/Maria_main_photo.jpg')
	with open ('Text/Greeting.txt', 'r', encoding='utf-8') as file:
		lines = file.readlines()
	first_message = f'Привет {message.from_user.first_name}!\n\n' + ''.join(lines)
	bot.send_photo(message.chat.id, photo=open(main_photo, 'rb'), caption=first_message,
				   reply_markup=markup)

@bot.message_handler(content_types=['text'])
def on_click(message):
	if message.text.lower() == '📋 описание услуг':
		service_description(message)
		# bot.send_message(message.chat.id, 'Описание услуг')
	elif message.text.lower() == '🖌️ о студии':
		studio_info(message)
		# bot.register_next_step_handler(message, studio_info)
	elif message.text.lower() == '💸 индивидуальный рассчет':
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
	pictures = types.InlineKeyboardButton(text = f'🖼️ Интерьерные картины'
														,callback_data='info_Интерьерные картины')
	about = types.InlineKeyboardButton('💁 Обо мне', callback_data='info_Обо мне')
	contacts = types.InlineKeyboardButton('📞 Контакты', callback_data='info_Контакты')
	# markup_info.add(about, contacts,pictures)
	markup_info.row(about, contacts)
	markup_info.row(pictures)
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
	full_project = types.InlineKeyboardButton('🗝️ Под ключ',callback_data='Дизайн-проект под ключ')
	project = types.InlineKeyboardButton('💥Дизайн-проект', callback_data='Дизайн-проект')
	express = types.InlineKeyboardButton('🚅 Экспресс', callback_data='Экспресс проект')
	project_about = types.InlineKeyboardButton('Подробнее чем отличаются услуги', callback_data='about_services')
	# markup.add(full_project, project,express, project_about)
	markup.row(full_project)
	markup.row(project,express)
	markup.row(project_about)
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
	user_data[message.from_user.id] = User(message.from_user.first_name)
	while True:
		global square
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

			column_names, rows = fetch_data_from_db(message)
			table = format_table(column_names, rows)
			send_table(message.chat.id, table)

			break
		except ValueError:
			bot.send_message(message.chat.id,'Неверный формат значения площади, введите число')
			personal_calc(message)
			break





bot.infinity_polling()