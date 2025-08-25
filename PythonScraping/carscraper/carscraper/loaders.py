from itemloaders.processors import MapCompose, TakeFirst
import logging
logger = logging.getLogger(__name__)
def TakeSecond(value):
    """Бере другий елемент зі списку, якщо є, інакше перший"""
    if len(value) >= 2:
        return value[1]
    else:
        return value[0] if value else None


def TakeNonEmpty(value):
    """Бере перший непорожній елемент зі списку"""
    for v in value:
        if v and v.strip() != '':
            return v.strip()
    return None


def clean_value(value):
    """Очищає значення від зайвих пробілів"""
    if value:
        return value.strip()
    return value


def choose_price(values):
    """
    values: список рядків, наприклад
      ['21 000 €', '38500', '1966785']
    або
      ['38500', '...']
    У першому випадку повинен повернути другий елемент (число доларів без знаку),
    у другому — перший (оскільки вже число доларів без знака).
    """
    if not values:
        return None

    first, *rest = values

    # Якщо в першому є '$' – беремо його
    if '$' in first:
        return first.strip()

    # Якщо перший містить 'грн' або '€' – беремо другий як число доларів
    if rest:
        return rest[0].strip()

    # Інакше – повертаємо перший (він уже число)
    return first.strip()

def clean_price(value):
    """
    Очищає строку від символів валюти та пробілів, повертає int.
    '47 154 $' -> 47154
    '1 966 785 грн' -> 1966785
    """
    if not value:
        return None
    s = str(value).replace('$', '').replace('грн', '').strip()
    import re
    digits = re.sub(r'[^\d]', '', s)
    return int(digits) if digits else None


def clean_odometer(value):
    """
    Конвертує пробіг з тисяч кілометрів в кілометри
    '95 тис. км' -> 95000
    """
    if not value:
        return None

    # Витягуємо число з початку рядка
    import re
    numbers = re.findall(r'\d+', str(value))
    if numbers:
        return int(numbers[0]) * 1000
    return None


def clean_image_count(value):
    """
    Очищає кількість зображень
    'з 13' -> 13, '1 з 13' -> 13
    """
    if not value:
        return None

    # Шукаємо числа в рядку
    import re
    numbers = re.findall(r'\d+', str(value))

    if len(numbers) >= 2:
        # Якщо є два числа, беремо друге (загальна кількість)
        return int(numbers[1])
    elif len(numbers) == 1:
        # Якщо одне число, беремо його
        return int(numbers[0])

    return None


def clean_car_number(value):
    """Очищає номерний знак від зайвих символів"""
    if not value:
        return None

    # Видаляємо зайві пробіли та символи
    return value.strip().upper()


def clean_car_vin(value):
    """Очищає VIN код"""
    if not value:
        return None

    # VIN код має бути 17 символів
    cleaned = value.strip().upper()
    if len(cleaned) == 17:
        return cleaned
    return cleaned  # Повертаємо як є, навіть якщо довжина не 17


def clean_username(value):
    """Очищує ім'я користувача"""
    if not value:
        return None

    # Видаляємо зайві пробіли та символи переносу рядка
    return value.strip().replace('\n', ' ').replace('\r', '')


def format_phone_number(phone):
    """
    Форматує номер телефону у міжнародний формат
    Приклад: (097) 1234567 -> 380971234567
    """
    if not phone:
        return None
        
    # Видаляємо всі нецифрові символи
    import re

    digits = re.sub(r'\D', '', str(phone))

    # Якщо номер починається з 0, замінюємо на 380
    if digits.startswith('0'):
        return int('38' + digits)
    # Якщо номер починається з 380, залишаємо як є
    elif digits.startswith('380'):
        return int(digits)
    # Якщо номер короткий (менше 9 цифр), вважаємо, що це місцевий номер
    elif len(digits) < 9:
        return int('380' + digits[-9:])
    # В інших випадках повертаємо цифри як є
    return int(digits)


def clean_phone_list(value):
    """
    Обробляє список телефонів та повертає найкращий варіант
    """
    if not value:
        return None

    if isinstance(value, list):
        # Фільтруємо порожні та невалідні номери
        valid_phones = []
        for phone in value:
            if phone and isinstance(phone, str):
                phone = phone.strip()
                if phone and phone not in ['Phone not available', 'Phone not found', 'Not available']:
                    # Перевіряємо чи містить цифри
                    import re
                    if re.search(r'\d', phone):
                        # Форматуємо номер після перевірки
                        formatted_phone = format_phone_number(phone)
                        valid_phones.append(formatted_phone)


        # Повертаємо перший валідний номер
        # return valid_phones[0] if valid_phones else None
        # return valid_phones

    # Якщо передано не список, а один номер
    # return format_phone_number(value)
        return valid_phones
    else:
        return format_phone_number(value)