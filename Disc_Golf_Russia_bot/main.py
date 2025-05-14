import aiogram
from aiogram import types
from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, BaseFilter
from aiogram.fsm.state import State, StatesGroup
from Keyboards.Inline_Russia import get_inline_keyboard_cources,get_inline_keyboard_region_parks,get_inline_keyboard_Russia, get_inline_keyboard_shops, get_inline_keyboard_regions
from Regions.Regions import Region,regions
import asyncio
import logging
import os
import datetime
from datetime import datetime
from pathlib import Path
from config import TOKEN

# Включаем логирование
logging.basicConfig(level=logging.INFO)
bot = aiogram.Bot(TOKEN)
# Диспетчер
dp = aiogram.Dispatcher()

project_path = Path(__file__).parent
Region.load_regions(regions)
region = None
park = None
project_path = Path(__file__).parent
city_list = str(f'Екатеринбург\n'
            f'Москва\n'
            f'Санкт-Петербург\n'
            f'Нижний Новгород\n'
            f'Белгород\n'
            f'Набережные Челны\n'
            f'Псков\n'
            f'Великие Луки\n'
            f'Рыбинск\n'
            f'Тольятти\n'
            f'Калининград\n')



class MainFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.text in ('Что такое диск-гольф','Диск-гольф в России','Правила диск-гольфа','Контакты')  # True, если текст — число

class Form(StatesGroup):
    waiting_region_code = State()


# Хэндлер на команду /start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    start_keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text='Что такое диск-гольф'), types.KeyboardButton(text='Правила диск-гольфа')],
            [types.KeyboardButton(text='Диск-гольф в России'), types.KeyboardButton(text='Контакты')]
        ],
        resize_keyboard=True
    )
    with open('Texts/Greeting.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    await message.answer(f'\n\n' + ''.join(lines),reply_markup=start_keyboard)
    # await message.answer('Здесь будет приветственное сообщение',
    #     reply_markup=start_keyboard)

@dp.message(MainFilter())
async def on_click(message: types.Message):
    if message.text.lower() == 'что такое диск-гольф':
        with open('Texts/WhatIs.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        await message.answer(f'\n\n' + ''.join(lines))
    elif message.text.lower() == 'правила диск-гольфа':
        with open('Texts/Rules.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        await message.answer(f'\n\n' + ''.join(lines))
    elif message.text.lower() == 'диск-гольф в россии':
        await message.answer(f'Здесь будет кратко о диск-гольфе в РФ\n'
                             f'появляются внутренние кнопки полезной инфы: ссылка на канал, сайт,\n' 
                             f'трассы для игры в регионах, расписание турниров',
                             reply_markup=get_inline_keyboard_Russia()
                             )
    elif message.text.lower() == 'контакты':
        with open('Texts/Contacts.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        await message.answer(f'\n\n' + ''.join(lines))

# Обработка нажатий на кнопки
@dp.callback_query(lambda c: c.data.startswith('russia_'))
async def handle_callback_(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()  #
    if callback_query.data == 'russia_shop':
        await callback_query.message.answer('Ссылки где купить диски и корзины',reply_markup=get_inline_keyboard_shops())
    elif callback_query.data == 'russia_regions':
        choose_region = f'Выберите регион, отправьте код интересующего Вас региона'
        region_code = str(Path(f'{project_path}/Regions/Region_list.jpeg'))
        await callback_query.message.answer(f'{city_list}\n\n'
                                            f'В этих городах из списка можно поиграть в диск-гольф\n'
                                            f'Введите название интересующего вас города')
        await state.set_state(Form.waiting_region_code)
    elif callback_query.data == 'russia_competitions':
        schedule_message = str('Расписание турниров на текущий сезон')
        schedule = str(Path(f'{project_path}/Расписание/{datetime.now().year}.jpg'))
        await callback_query.message.answer_photo(photo=types.FSInputFile(schedule), caption=schedule_message)
        # Устанавливаем состояние ожидания кода региона
        # await state.set_state(Form.waiting_region_code)
    elif callback_query.data == 'russia_partners':
        with open('Texts/Partnership.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        await callback_query.message.answer(f'\n\n' + ''.join(lines))

@dp.message(Form.waiting_region_code)
async def regions_menu(message: types.Message, state: FSMContext):
    try:
        if message.text.lower().strip():  # Сравниваем строку со строкой
            global region
            region = message.text.lower()
            current_region = Region.get(region)
            keyboard = get_inline_keyboard_regions(message.text.lower())
            await message.answer(f'Вы в меню региона {current_region.fullname}',reply_markup=keyboard)
            await state.clear()  # Сбрасываем состояние
        else:
            await message.answer("В этом городе пока нет диск-гольф парка")
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("К сожалению в вашем городе еще нет диск-гольф парка")

@dp.callback_query(lambda c: c.data.startswith('region_'))
async def handle_callback_(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'region_Где поиграть, трассы':
        keyboard = get_inline_keyboard_region_parks(region)
        await callback_query.message.answer(f'Выберите парк',reply_markup=keyboard)
    elif callback_query.data == 'region_Расписание турниров':

        schedule_message = str('Расписание турниров на текущий сезон')
        schedule = str(Path(f'{project_path}/Regions/{region.lower()}/Расписание/{datetime.now().year}.jpg'))
        print(schedule)
        await callback_query.message.answer_photo(photo=types.FSInputFile(schedule), caption=schedule_message)


@dp.callback_query(lambda c: c.data.startswith('park_'))
async def handle_callback_(callback_query: types.CallbackQuery):
     global park
     park = callback_query.data[5:]
     keyboard = get_inline_keyboard_cources(region, callback_query.data[5:])
     await callback_query.message.answer(f'Парк {callback_query.data[5:]}',reply_markup=keyboard)

async def send_location(message: types.Message, parkname, latitude, longitude):
    global park
    current_region = Region.get(region)
    lat = latitude   # широта
    long = longitude  # долгота
    await message.answer(f'Диск-гольф парк {park}\n' 
                         f'Адрес: {parkname["address"]}\n\n'
                         f'Нажмите на геолокацию ниже')
    await bot.send_location(chat_id=message.chat.id, latitude=lat, longitude=long)

@dp.callback_query(lambda c: c.data.startswith('cources_'))
async def handle_callback_(callback_query: types.CallbackQuery):
    global park, region
    if callback_query.data == 'cources_Геолокация парка':
         current_region = Region.get(region)
         if park in current_region.park:
             park_dict = current_region.park[park]
             lat = park_dict['latitude']  # Получаем значение latitude
             long = park_dict['longitude']  # Получаем значение latitude
             await send_location(callback_query.message,park_dict,lat,long)
         else:
             await callback_query.message.answer(f"Парк {park} не найден в регионе.")
    elif callback_query.data == 'cources_Схемы лэйаутов':
        try:
            folder_path = str(Path(f'{project_path}/Regions/{region.lower()}/{park}'))
            files = os.listdir(folder_path)
            if not files:
                await callback_query.message.answer(f'Схемы в разработке')
            for file in files:
                full_file_path = str(Path(f'{folder_path}/{file}'))
                file_name_without_extension = os.path.splitext(os.path.basename(full_file_path))[0]
                await callback_query.message.answer_photo(photo=types.FSInputFile(full_file_path), caption=file_name_without_extension)
        except FileNotFoundError:
            await callback_query.message.answer(f'Схемы в разработке')
# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
