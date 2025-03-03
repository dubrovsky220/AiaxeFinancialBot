from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

commands_handlers_router = Router()


@commands_handlers_router.message(CommandStart())
async def start_command(message: Message):
    """Processes /start command sent by a user"""
    logger.debug(f'User with telegram_id={message.from_user.id} used command /start')
    await message.answer(f'Hello, {message.from_user.first_name}')
