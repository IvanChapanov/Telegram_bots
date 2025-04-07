import aiogram
from aiogram import types
from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, BaseFilter
from aiogram.fsm.state import State, StatesGroup
from Keyboards.Inline_Russia import get_inline_keyboard_Russia, get_inline_keyboard_shops, get_inline_keyboard_regions
from Regions.Regions import Region,regions
import asyncio
import logging
import os
import datetime
from pathlib import Path
from config import TOKEN

# Включаем логирование
logging.basicConfig(level=logging.INFO)
bot = aiogram.Bot(TOKEN)
# Диспетчер
dp = aiogram.Dispatcher()

Region.load_regions(regions)
region = None
project_path = Path(__file__).parent

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

    await message.answer('Здесь будет приветственное сообщение',
        reply_markup=start_keyboard)

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
        await callback_query.message.answer_photo(photo=types.FSInputFile(region_code), caption=choose_region)
        await state.set_state(Form.waiting_region_code)

        # Устанавливаем состояние ожидания кода региона
        # await state.set_state(Form.waiting_region_code)

@dp.message(Form.waiting_region_code)
async def regions_menu(message: types.Message, state: FSMContext):
    try:
        if message.text.strip() == "66":  # Сравниваем строку со строкой
            current_region = Region.get(message.text)
            keyboard = get_inline_keyboard_regions(message.text)
            await message.answer(f'Вы в меню региона {current_region.name}',reply_markup=keyboard)
            await state.clear()  # Сбрасываем состояние
        else:
            await message.answer("Пожалуйста, введите правильный код региона (66)")
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Произошла ошибка при обработке запроса")

@dp.callback_query(lambda c: c.data.startswith('region_'))
async def handle_callback_(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'region_Где поиграть, трассы':
        await send_location(callback_query.message)
    elif callback_query.data == 'region_Схемы трасс':
        await callback_query.message.answer('Сообщение с файлами схемы трасс')
    elif callback_query.data == 'region_Канал Telegram':
        await callback_query.message.answer('Сообщение с файлами схемы трасс')

async def send_location(message: types.Message):
    latitude = 56.773543   # широта (Уктус)
    longitude = 60.649179  # долгота (Уктус)
    await message.answer('Диск-гольф парк Уктус')
    await bot.send_location(chat_id=message.chat.id, latitude=latitude, longitude=longitude)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
