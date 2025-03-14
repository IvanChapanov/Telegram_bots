from curses.ascii import isdigit
import telebot
from telebot import types
import datetime
from config import TOKEN
import json
import psycopg2

bot = telebot.TeleBot(TOKEN)


user_data = {}

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

first_message_id = None

def fetch_new_data_from_db():
	conn = psycopg2.connect(
		dbname=db_config['dbname'],
		user=db_config['user'],
		password=db_config['password'],
		host=db_config['host'],
		port=db_config['port']
	)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM v_new_users_request')
	rows = cursor.fetchall()
	column_names = [i[0] for i in cursor.description]
	return column_names, rows

def fetch_all_data_from_db():
	conn = psycopg2.connect(
		dbname=db_config['dbname'],
		user=db_config['user'],
		password=db_config['password'],
		host=db_config['host'],
		port=db_config['port']
	)
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM v_all_users_request')
	rows = cursor.fetchall()
	column_names = [i[0] for i in cursor.description]
	return column_names, rows

def format_table(column_names, rows):
	# Форматируем таблицу
	table = ''

	# Добавляем шапку
	table += " | ".join(column_names) + "\n"
	table += "-" * (len(column_names) * 18) + "\n"  # Разделитель на основе длины шапки

	# Добавляем строки данных
	for row in rows:
		table += " | ".join(map(str, row)) + "\n"
	return table

def user_status_update():
	conn = psycopg2.connect(
		dbname=db_config['dbname'],
		user=db_config['user'],
		password=db_config['password'],
		host=db_config['host'],
		port=db_config['port']
	)
	cursor = conn.cursor()
	cursor.execute('UPDATE dbo.users SET viewed = 1 WHERE viewed IS NULL')
	conn.commit()

def send_table(chat_id, table):
	bot.send_message(chat_id, f"<pre>{table}</pre>", parse_mode='HTML')

def get_new_data(message):
	column_names, rows = fetch_new_data_from_db()
	table = format_table(column_names, rows)
	send_table(message.chat.id, table)

def get_all_data(message):
	column_names, rows = fetch_all_data_from_db()
	table = format_table(column_names, rows)
	send_table(message.chat.id, table)

message_ids = []

# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
# 	message_ids.append(message.message_id)

@bot.message_handler(commands=['start'])
def start_message(message):
	global first_message_id
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	check_new_user_btn = types.KeyboardButton('🆕 Вывести список новых пользователей')
	table_read_btn = types.KeyboardButton('✔️ Отметить новых как просмотренные')
	check_all_user_btn = types.KeyboardButton('👩🏻‍💻 Вывести список всех пользователей')
	markup.row(check_new_user_btn)
	markup.row(table_read_btn)
	markup.row(check_all_user_btn)
	with open ('start.txt', 'r', encoding='utf-8') as file:
		lines = file.readlines()
	first_message = ''.join(lines)
	new_start_message = bot.send_message(message.chat.id, first_message,
					 reply_markup=markup)
	first_message_id = new_start_message.message_id


def clear_chat(message):
# Удаляем все сообщения, кроме первого
	for msg in message_ids:
		# Пропускаем первое сообщение
		if msg != first_message_id:
			bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

@bot.message_handler(content_types=['text'])
def on_click(message):
	if message.text.lower() == '🆕 вывести список новых пользователей':
		# clear_chat(message)
		get_new_data(message)
		# bot.send_message(message.chat.id, 'Описание услуг')
	elif message.text.lower() == '✔️ отметить новых как просмотренные':
		# clear_chat(message)
		user_status_update()
		bot.send_message(message.chat.id, 'Все запросы пользователей отмечены как просмотренные')
	elif message.text.lower() == '👩🏻‍💻 вывести список всех пользователей':
		# clear_chat(message)
		get_all_data(message)
	else:
		# clear_chat(message)
		bot.send_message(message.chat.id, f'Выбери действие из меню')

bot.infinity_polling()