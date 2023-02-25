from aiogram import types
import requests

products_dict = {}


def category_product_dict():
    """Возвращает словарь типа:
    {Камеры [{'name': 'Детский цифровой ,
    'article': '194830587', 'description': '', 'photos': ['none']}, {'category_pk': 3]}, ...[]}
    """
    global products_dict
    if len(products_dict) == 0:
        url = f"http://185.105.88.151/products/product_dict"
        # url = f"http://127.0.0.1:8000/products/product_dict"
        response = requests.get(url)
        products_dict = response.json()
    return products_dict


def category_keyboard():
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
    category_pk = category_product_dict()[category][-1]['category_pk']
    for product in category_product_dict()[category]:
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
