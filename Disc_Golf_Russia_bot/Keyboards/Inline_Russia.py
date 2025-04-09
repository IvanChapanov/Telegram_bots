import aiogram
import sys
import os
from pathlib import Path
from aiogram import types
# from Disc_Golf_Russia_bot.Regions.Regions import Region,regions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Regions.Regions import *

Region.load_regions(regions)
region = None

def get_inline_keyboard_Russia():
    inline_kb_list = [
        [types.InlineKeyboardButton(text='Канал Диск-гольф РФ', url='https://t.me/discgolf_russia')],
        [types.InlineKeyboardButton(text='Сайт Диск-гольф РФ', url='https://rdga.ru/')],
        [types.InlineKeyboardButton(text='География диск-гольфа в России', callback_data='russia_regions')],
        [types.InlineKeyboardButton(text='Расписание федеральных турниров', callback_data='russia_competitions')],
        [types.InlineKeyboardButton(text='Купить диски и инвентарь', callback_data='russia_shop')],
        [types.InlineKeyboardButton(text='Партнёрам и спонсорам', callback_data='russia_partners')]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def get_inline_keyboard_shops():
    inline_kb_list = [
        [types.InlineKeyboardButton(text='Диски магазин Ahoy', url='https://ahoydiscs.ru/')],
        [types.InlineKeyboardButton(text='Канал Продажа/обмен диск-гольф дисками',
                                    url='https://t.me/dgdisc')],
        [types.InlineKeyboardButton(text='Канал Диски на продажу (Никита)',
                                    url='https://t.me/discshopnik')],
        [types.InlineKeyboardButton(text='Корзины Владимир Ли г.Белгород', url='https://t.me/Vladimirli1')],
        [types.InlineKeyboardButton(text='Корзины Александр Макаров г.Нижний Новгород', url='https://t.me/makarov_discgolf')],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def get_inline_keyboard_regions(name):
    current_region = Region.get(name)
    inline_kb_list = [
        [types.InlineKeyboardButton(text=f'{current_region.shortname} - Где поиграть, трассы', callback_data='region_Где поиграть, трассы')],
        [types.InlineKeyboardButton(text=f'{current_region.shortname} - Расписание турниров', callback_data='region_Расписание турниров')],
        [types.InlineKeyboardButton(text=f'{current_region.shortname} - Канал Telegram', url = current_region.region_channel,callback_data='region_Канал Telegram')],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def get_inline_keyboard_region_parks(name):
    # Создаем клавиатуру
    current_region = Region.get(name)
    inline_kb_list = []

    # Извлекаем названия парков и создаем кнопки для каждого из них
    for park_name in current_region.park.keys():
        inline_kb_list.append(
        [
        types.InlineKeyboardButton(text=f'{current_region.shortname} - {park_name}', callback_data=f'park_{park_name}')
        ]
        )
    return types.InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def get_inline_keyboard_cources(region,name):
    current_region = Region.get(region)
    park_dict = current_region.park[name]
    inline_kb_list = [
        [types.InlineKeyboardButton(text=f'{name} - Геолокация парка', callback_data='cources_Геолокация парка')],
        [types.InlineKeyboardButton(text=f'{name} - Схемы лэйаутов', callback_data='cources_Схемы лэйаутов')],
        [types.InlineKeyboardButton(text=f'{name} - Ссылка на трассу в Metrix',
                                    url=park_dict['metrix_link'], callback_data='cources_Ссылка Metrix')],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_kb_list)