from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger

from handlers.menu_processing import get_main_page
from keyboards.inline import MenuCallBack

commands_handlers_router = Router()


@commands_handlers_router.message(CommandStart())
async def start_command(message: Message):
    """Handles /start command sent by a user"""

    logger.debug(f'User with telegram_id={message.from_user.id} used command /start')
    text, keyboard_markup = get_main_page(level=0, menu_name='main')
    await message.answer(f'Hello, {message.from_user.first_name}', reply_markup=keyboard_markup)


@commands_handlers_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallBack):
    """Handles clicks on inline menu buttons"""

    logger.debug(f'User with telegram_id={callback.from_user.id} clicked menu button')
    text, keyboard_markup = get_main_page(level=callback_data.level, menu_name=callback_data.menu_name)
    await callback.message.edit_text(text=text, reply_markup=keyboard_markup)
    await callback.answer()
