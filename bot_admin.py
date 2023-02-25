from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import sqlite3

from settings import TEL_TOKEN, ADMIN_LIST
from bot_client import category_keyboard, text_for_message

tel_token = TEL_TOKEN
admin_list = ADMIN_LIST

# Обьявляем переменные
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылка"))
kb.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
kb.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
kb.add(types.InlineKeyboardButton(text="Статистика"))
kb.add(types.InlineKeyboardButton(text="Витрина магазина Benefittime"))

kb_client = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(types.InlineKeyboardButton(text="витрина"))

# Инициализируем проект
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=tel_token)
dp = Dispatcher(bot, storage=storage)

# Создаем Базу Данных
conn = sqlite3.connect('db.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER, block INTEGER);""")
conn.commit()


# Обьявляем States
class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()
    product_category = State()


# Обработка команды "/start"
@dp.message_handler(commands=['start'])
async def start(message: Message):
    cur = conn.cursor()
    cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
    result = cur.fetchone()
    if message.from_user.id in admin_list:
        await message.answer('Добро пожаловать в Админ-Панель! Выберите действие на клавиатуре', reply_markup=kb)
    else:
        if result is None:
            cur = conn.cursor()
            cur.execute(f'''SELECT * FROM users WHERE (user_id="{message.from_user.id}")''')
            entry = cur.fetchone()
            if entry is None:
                cur.execute(f'''INSERT INTO users VALUES ('{message.from_user.id}', '0')''')
                conn.commit()
                await message.answer('Привет')
        else:
            await message.answer('Ты был заблокирован!')


# обработаем кнопку "Рассылка"
@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: Message):
    await dialog.spam.set()
    await message.answer('Напиши текст рассылки')


# обработаем этот текст и отправим его пользователям
@dp.message_handler(state=dialog.spam)
async def start_spam(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Главное меню', reply_markup=kb)
        await state.finish()
    else:
        cur = conn.cursor()
        cur.execute(f'''SELECT user_id FROM users''')
        spam_base = cur.fetchall()
        for z in range(len(spam_base)):
            await bot.send_message(spam_base[z][0], message.text)
            await message.answer('Рассылка завершена', reply_markup=kb)
            await state.finish()


# добавление пользователей в ЧС
@dp.message_handler(content_types=['text'], text='Добавить в ЧС')
async def hanadler(message: types.Message, state: FSMContext):
    if message.chat.id in admin_list:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer('Введите id пользователя, которого нужно заблокировать.\nДля отмены нажмите кнопку ниже', reply_markup=keyboard)
        await dialog.blacklist.set()


# будем банить пользователей
@dp.message_handler(state=dialog.blacklist)
async def proce(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Отмена! Возвращаю назад.', reply_markup=kb)
        await state.finish()
    else:
        if message.text.isdigit():
            cur = conn.cursor()
            cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
            result = cur.fetchall()
            if len(result) == 0:
                await message.answer('Такой пользователь не найден в базе данных.', reply_markup=kb)
                await state.finish()
            else:
                a = result[0]
                id = a[0]
                if id == 0:
                    cur.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
                    conn.commit()
                    await message.answer('Пользователь успешно добавлен в ЧС.', reply_markup=kb)
                    await state.finish()
                    await bot.send_message(message.text, 'Ты был забанен Администрацией')
                else:
                    await message.answer('Данный пользователь уже получил бан', reply_markup=kb)
                    await state.finish()
        else:
            await message.answer('Ты вводишь буквы...\n\nВведи ID')


# Удалять пользователей из ЧС
@dp.message_handler(content_types=['text'], text='Убрать из ЧС')
async def hfandler(message: types.Message, state: FSMContext):
    cur = conn.cursor()
    cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
    result = cur.fetchone()
    if result is None:
        if message.chat.id in admin_list:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.InlineKeyboardButton(text="Назад"))
            await message.answer('Введите id пользователя, которого нужно разблокировать.\nДля отмены нажмите кнопку ниже', reply_markup=keyboard)
            await dialog.whitelist.set()


@dp.message_handler(state=dialog.whitelist)
async def proc(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Отмена! Возвращаю назад.', reply_markup=kb)
        await state.finish()
    else:
        if message.text.isdigit():
            cur = conn.cursor()
            cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
            result = cur.fetchall()
            conn.commit()
            if len(result) == 0:
                await message.answer('Такой пользователь не найден в базе данных.', reply_markup=kb)
                await state.finish()
            else:
                a = result[0]
                id = a[0]
                if id == 1:
                    cur = conn.cursor()
                    cur.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
                    conn.commit()
                    await message.answer('Пользователь успешно разбанен.', reply_markup=kb)
                    await state.finish()
                    await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
                else:
                    await message.answer('Данный пользователь не получал бан.', reply_markup=kb)
                    await state.finish()
        else:
            await message.answer('Ты вводишь буквы...\n\nВведи ID')


# добавим статистику для нашего бота
@dp.message_handler(content_types=['text'], text='Статистика')
async def hfandler(message: types.Message, state: FSMContext):
    cur = conn.cursor()
    cur.execute('''select * from users''')
    results = cur.fetchall()
    await message.answer(f'Людей которые когда либо заходили в бота: {len(results)}')


@dp.message_handler(content_types=['text'])  # , text='витрина')
async def spam(message: Message):
    await dialog.product_category.set()
    await message.answer('Представляю Вашему вниманию витрину магазина Benefittime. '
                         'Нажмите на интересующую категорию:', reply_markup=category_keyboard())


@dp.message_handler(state=dialog.product_category)
async def proc(message: types.Message, state: FSMContext):
    stop_list = ['STOP', 'Stop', 'stop']
    if message.text in stop_list:
        await state.finish()
        if message.from_user.id in admin_list:
            await message.answer('Добро пожаловать в Админ-Панель! Выберите действие на клавиатуре', reply_markup=kb)
        else:
            await message.answer('Возвращайтесь', reply_markup=kb_client)
    else:
        for text_message in text_for_message(message.text):
            await message.answer(text_message, reply_markup=category_keyboard(), parse_mode='HTML', disable_web_page_preview=text_message[1])
    # await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
