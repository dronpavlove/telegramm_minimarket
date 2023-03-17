from aiogram import types
from aiogram.utils.callback_data import CallbackData
import requests
import time
from settings import horo_data, day_data
from bs4 import BeautifulSoup as Soup

callback_horo = CallbackData("post", "id", "action")
products_dict = {}
timer = 0


def edit_timer(period=24):
    """
    Определяет периодичность обновления глобальных переменных
    По умолчанию 24 часа
    """
    global timer
    current_time = int(time.strftime('%H', time.localtime()))
    if current_time > timer:
        difference = current_time - timer
    else:
        difference = 24 - timer + current_time
    if difference >= period:
        timer = current_time
        return True
    else:
        return False


def category_product_dict(upd=False):
    """Возвращает словарь типа:
    {Камеры [{'name': 'Детский цифровой ,
    'article': '194830587', 'description': '', 'photos': ['none']}, {'category_pk': 3]}, ...[]}
    """
    global products_dict
    if len(products_dict) == 0 or edit_timer() is True or upd is True:
        url = f"http://185.105.88.151/products/product_dict"
        # url = f"http://127.0.0.1:8000/products/product_dict"
        response = requests.get(url)
        products_dict = response.json()
    return products_dict


def category_keyboard():
    """
    Формирует клавиатуру из существующих
    категорий товаров на сайте Benefittime
    :return:
    """
    keyboard = []
    inline_keyboard = []
    num = 1
    category_list = [key for key in category_product_dict().keys()]
    for category in category_list:
        if num % 3 != 0:
            inline_keyboard.append(types.KeyboardButton(category))
        else:
            inline_keyboard.append(types.KeyboardButton(category))
            keyboard.append(inline_keyboard)
            inline_keyboard = []
        num += 1
    keyboard.append(inline_keyboard)
    keyboard.append(["STOP"])
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    return reply_markup


def text_for_message(category: str):
    """
    Отдаёт текстовые сообщения о товарах выбранной категории для
    транслирования в сообщениях телеграмм в формате HTML
    """
    category_pk = category_product_dict()[category][-1]['category_pk']
    for product in category_product_dict()[category][:4]:
        if not 'category_pk' in product:
            text_message = f'<b>{product["name"]}</b>\n' \
                           f'<b>{product["article"]}</b>\n' \
                           f'<i>{product["description"]}</i>\n'
            photo = 'http://185.105.88.151/static/default.png'
            if product["photos"][0] != 'none':
                text_message += f'<a href="http://185.105.88.151/products/category/{category_pk}">На сайт beneffittime</a>\n\n'
                photo = f'http://185.105.88.151/media/{product["photos"][0]}'
            text_message += photo
            yield text_message


def horo_list():
    """
    Возвращает клавиатуру из кнопок ЗНАКИ ГОРОСКОПА
    :return:
    """
    markup = types.InlineKeyboardMarkup(row_width=4)
    count = 0
    keyboard_list = []
    for key, value in horo_data.items():
        count += 1
        button = types.InlineKeyboardButton(key, callback_data=callback_horo.new(id=value, action='horo'))
        keyboard_list.append(button)
        if count % 4 == 0:
            markup.row(keyboard_list[0], keyboard_list[1], keyboard_list[2], keyboard_list[3])
            keyboard_list = []
    return markup


def horo_detail(horo_name, day='today'):
    """
    Получает по нажатию кнопки название знака из гороскопа и период.
    Возвращает текст из mail horo
    :param horo_name:
    :param day:
    :return:
    """
    markup = types.InlineKeyboardMarkup(row_width=4)
    keyboard_list = list()
    text = str()
    ru_horo_name = str()
    for key, value in horo_data.items():
        if horo_name == value:
            ru_horo_name = key
    url = f"https://horo.mail.ru/prediction/{horo_name}/{day}/"
    response = requests.get(url)
    res = response.text
    for key, value in day_data.items():
        if value == day:
            text = f'<b>{key}, {ru_horo_name}\n</b>'
        else:
            button = types.InlineKeyboardButton(
                key, callback_data=callback_horo.new(
                    id=value + f',{horo_name}', action='day'
                )
            )
            keyboard_list.append(button)
    markup.row(*keyboard_list)
    markup.row(types.InlineKeyboardButton('Завершить работу гороскопа',
                                          callback_data=callback_horo.new(
                                              id='horo_stop', action='horo')
                                          )
               )
    for i in Soup(res, 'html.parser').find_all('p'):
        text += f'<i>{str(i)[3:-4:]}</i>'
    return text, markup
