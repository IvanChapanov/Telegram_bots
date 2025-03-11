from curses.ascii import isdigit
import telebot
from telebot import types
import sys
import datetime
import mysql.connector
from mysql.connector import errorcode
from config import TOKEN
import json

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
try:
	db = mysql.connector.connect(
		host=db_config['host'],
		port=db_config['port'],
		user=db_config['user'],
		password=db_config['password'],
		database=db_config['dbname']
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

def fetch_new_data_from_db():
	cursor.execute('SELECT * FROM v_new_users_request')
	rows = cursor.fetchall()
	column_names = [i[0] for i in cursor.description]
	return column_names, rows

def fetch_all_data_from_db():
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
	cursor.execute('UPDATE dbo.users SET viewed = 1 WHERE viewed IS NULL')
	db.commit()

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

@bot.message_handler(commands=['start'])
def start_message(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	check_new_user_btn = types.KeyboardButton('🆕 Вывести список новых пользователей')
	table_read_btn = types.KeyboardButton('✔️ Отметить новых как просмотренные')
	check_all_user_btn = types.KeyboardButton('👩🏻‍💻 Вывести список всех пользователей')
	markup.row(check_new_user_btn)
	markup.row(table_read_btn)
	markup.row(check_all_user_btn)
	bot.send_message(message.chat.id, f'Список пользователей выполнивших индивидуальный рассчет',
					 reply_markup=markup)

@bot.message_handler(content_types=['text'])
def on_click(message):
	if message.text.lower() == '🆕 вывести список новых пользователей':
		get_new_data(message)
		# bot.send_message(message.chat.id, 'Описание услуг')
	elif message.text.lower() == '✔️ отметить новых как просмотренные':
		user_status_update()
		bot.send_message(message.chat.id, 'Все запросы пользователей отмечены как просмотренные')
	elif message.text.lower() == '👩🏻‍💻 вывести список всех пользователей':
		get_all_data(message)
	else:
		bot.send_message(message.chat.id, f'Выбери действие из меню')

bot.infinity_polling()