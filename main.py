import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, Message
from dotenv import load_dotenv, find_dotenv
from loguru import logger

from database.engine import drop_db, create_db

# Loading environment variables
load_dotenv(find_dotenv())

# Initializing Bot abd Dispatcher
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())


def configure_logger(level: str):
    """Performs the initial configuration of the logger"""
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'logs.log')
    logger.add(
        log_file_path,
        format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}',
        level=level,
        rotation='10 MB',
    )


async def set_default_commands():
    """Sets default bot commands"""
    commands = [BotCommand(command='start', description='Запустить бота')]
    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())


async def on_startup():
    """The function is performed on bot startup"""
    await set_default_commands()
    # Deleting pending updates on bot startup
    await bot.delete_webhook(drop_pending_updates=True)

    run_param = False
    if run_param:
        await drop_db()
    await create_db()

    logger.info('Bot started successfully!')


@dp.message(CommandStart())
async def start_command(message: Message):
    logger.debug(f'User with telegram_id={message.from_user.id} used command /start')
    await message.answer(f'Hello, {message.from_user.first_name}')


async def main():
    configure_logger('DEBUG')

    dp.startup.register(on_startup)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (SystemExit, KeyboardInterrupt):
        logger.critical('Bot stopped!')
    except Exception as e:
        logger.critical(f'Bot stopped with exception: {e}')
