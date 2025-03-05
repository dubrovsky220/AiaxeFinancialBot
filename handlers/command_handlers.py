from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_user
from handlers.menu_processing import get_main_page
from keyboards.inline import MenuCallBack

commands_handlers_router = Router()


@commands_handlers_router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession):
    """Handles /start command sent by a user"""

    logger.debug(f'User with telegram_id={message.from_user.id} used command /start')

    is_user_created = await orm_add_user(session,
                                         telegram_id=message.from_user.id,
                                         first_name=message.from_user.first_name,
                                         last_name=message.from_user.last_name)

    text, keyboard_markup = get_main_page(session=session, level=0, menu_name='main')

    if is_user_created:
        # TODO Write welcome text in separate file
        await message.answer(f'Hello, {message.from_user.first_name}', reply_markup=keyboard_markup)
    else:
        # TODO Create function fetching statistics from database and formatting message with statistics
        await message.answer('Example statistics', reply_markup=keyboard_markup)


@commands_handlers_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    """Handles clicks on inline menu buttons"""

    logger.debug(f'User with telegram_id={callback.from_user.id} clicked menu button')
    text, keyboard_markup = get_main_page(session=session, level=callback_data.level, menu_name=callback_data.menu_name)
    await callback.message.edit_text(text=text, reply_markup=keyboard_markup)
    await callback.answer()
