import aiogram
from aiogram import types
from aiogram.filters.command import Command
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

# Хэндлер на команду /start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    start_keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text='Что такое диск-гольф'), types.KeyboardButton(text='Правила диск-гольфа')],
            [types.KeyboardButton(text='Диск_гольф в России'), types.KeyboardButton(text='Контакты')]
        ],
        resize_keyboard=True
    )

    await message.answer('Здесь будет приветственное сообщение',
        reply_markup=start_keyboard)


@dp.message(aiogram.F.content_type == types.ContentType.TEXT)
async def on_click(message: types.Message):
    if message.text.lower() == 'что такое диск-гольф':
        await message.answer('Здесь будет краткое описание что такое диск-гольф')
    elif message.text.lower() == 'правила диск-гольфа':
        await message.answer('Здесь будет краткое описание правил диск-гольфа')
    elif message.text.lower() == 'диск_гольф в россии':\
        await message.answer(f'Здесь будет о текущем развитии диск-гольфа в РФ\n'
                             f'появляются внутренник кнопки: ссылка на канал, сайт,\n' 
                             f'трассы для игры в регионах, расписание турниров')
    elif message.text.lower() == 'контакты':
        await message.answer('Здесь будет контактная информация и текст для патнеров')


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
