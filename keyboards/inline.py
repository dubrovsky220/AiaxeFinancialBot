from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix='menu'):
    """Class for menu callback data"""
    level: int
    menu_name: str


def get_main_menu_buttons(*, level: int, sizes: tuple[int, ...] = (2,)) -> InlineKeyboardMarkup:
    """
    Returns main menu inline keyboard
    :param level: menu level
    :param sizes: size of keyboard, 2-d tuple
    :return: inline keyboard markup
    """

    keyboard = InlineKeyboardBuilder()
    buttons = {
        'Добавить расход': 'add_expense',
        'Добавить доход': 'add_income',
        'Категории': 'categories',
        'Лимиты': 'limits',
        'История': 'history',
        'Статистика': 'statistics',
    }

    for text, menu_name in buttons.items():
        keyboard.add(InlineKeyboardButton(
            text=text, callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()
        ))

    return keyboard.adjust(*sizes).as_markup()
