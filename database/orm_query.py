from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.model import User


async def orm_add_user(
        session: AsyncSession,
        telegram_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
) -> bool:
    """Tries to add a new user to the User table. Returns True if added successfully. Returns False if user with specified telegram_id already exists."""

    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)

    if result.first() is None:
        try:
            session.add(
                User(telegram_id=telegram_id, first_name=first_name, last_name=last_name)
            )
            await session.commit()
            logger.debug(f'User with telegram_id={telegram_id} added to Users')
            return True
        except SQLAlchemyError as e:
            logger.error(f'Error when adding a new user to Users: {e}')

    logger.debug(f'User with telegram_id={telegram_id} already exists in Users')
    return False
