from key import token, token_demo, admin_list
from pozhelaniya import pozhelaniya
from aelita import aelita

TEL_TOKEN = token
ADMIN_LIST = admin_list

horo_data = {
            'Овен': 'aries', 'Телец': 'taurus', 'Близнецы': 'gemini',
            'Рак': 'cancer', 'Лев': 'leo', 'Дева': 'virgo',
            'Весы': 'libra', 'Скорпион': 'scorpio', 'Водолей': 'aquarius',
            'Стрелец': 'sagittarius', 'Козерог': 'capricorn', 'Рыбы': 'pisces',

        }
day_data = {
    'На сегодня': 'today',
    'На завтра': 'tomorrow',
    'На неделю': 'week',
    'На месяц': 'month'
}

books_data = {
    f'Пожелания: {len(pozhelaniya)} страниц по 19 строк': pozhelaniya,
    f'Аэлита: {len(aelita)} страниц по 19 строк': aelita
}
