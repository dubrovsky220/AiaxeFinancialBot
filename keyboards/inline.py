from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder


class MenuCallBack(CallbackData, prefix='menu'):
    """Class for menu callback data"""
    level: int = 0
    menu_name: str = 'main'
    category: Optional[str] = None
    action: Optional[str] = None


def get_main_menu_buttons(*, level: int, sizes: tuple[int, ...] = (2,)) -> InlineKeyboardMarkup:
    """
    Returns main menu inline keyboard
    :param level: menu level
    :param sizes: size of keyboard
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


def get_cancel_button() -> InlineKeyboardMarkup:
    """Returns inline keyboard markup with button 'Отмена'"""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Отмена ❌', callback_data=MenuCallBack(level=0, menu_name='main').pack()))

    return keyboard.as_markup()


def get_category_list_buttons(*,
                              categories: list[str],
                              level: int,
                              menu_name: str,
                              create_add_button: bool = False,
                              sizes: tuple[int, ...] = (2,)
                              ) -> InlineKeyboardMarkup:
    """
    Returns inline keyboard with categories
    :param categories: list of category names
    :param level: menu level
    :param menu_name: menu name
    :param create_add_button: if True, 'Добавить' button will be added to the keyboard
    :param sizes: size of keyboard
    :return: inline keyboard markup
    """

    keyboard = InlineKeyboardBuilder()

    if create_add_button:
        keyboard.add(InlineKeyboardButton(
            text='Добавить ➕', callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()
        ))

    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category, callback_data=MenuCallBack(level=level + 1, menu_name=menu_name, category=category).pack()
        ))

    keyboard.add(InlineKeyboardButton(
        text='Отмена ❌', callback_data=MenuCallBack(level=0, menu_name='main').pack()
    ))

    return keyboard.adjust(*sizes).as_markup()


def get_skip_buttons() -> InlineKeyboardMarkup:
    """Returns inline keyboard markup with buttons 'Пропустить' and 'Отмена'"""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Пропустить ▶', callback_data=MenuCallBack(action='skip').pack())
    )
    keyboard.add(
        InlineKeyboardButton(text='Отмена ❌', callback_data=MenuCallBack(level=0, menu_name='main').pack())
    )

    return keyboard.adjust(1).as_markup()


def get_save_buttons() -> InlineKeyboardMarkup:
    """Returns inline keyboard markup with buttons 'Сохранить' and 'Отмена'"""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Сохранить ✅', callback_data=MenuCallBack(action='save').pack())
    )
    keyboard.add(
        InlineKeyboardButton(text='Отмена ❌', callback_data=MenuCallBack(level=0, menu_name='main').pack())
    )

    return keyboard.adjust(1).as_markup()
