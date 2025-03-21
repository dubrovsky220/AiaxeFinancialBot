from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from database.model import User, CategoryIncome, CategoryExpense, Income, Expense


async def orm_get_user_id(session: AsyncSession, telegram_id: int) -> Mapped[int]:
    """Gets user id by telegram_id"""

    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    user_id = result.scalar().id
    return user_id


async def orm_add_default_categories(
        session: AsyncSession,
        *,
        telegram_id: int,
        income_categories: list[str],
        expense_categories: list[str],
):
    """Adds default categories of incomes and expenses for a new user"""

    user_id = orm_get_user_id(session, telegram_id)

    for category in income_categories:
        session.add(
            CategoryIncome(name=category, user_id=user_id)
        )

    for category in expense_categories:
        session.add(
            CategoryExpense(name=category, user_id=user_id)
        )

    try:
        await session.commit()
        logger.debug(f'Default categories of incomes and expenses were added to user with telegram_id={telegram_id}')
    except SQLAlchemyError as e:
        logger.error(f'Error when adding default categories of incomes and expenses: {e}')


async def orm_add_user(
        session: AsyncSession,
        *,
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

            # TODO Move categories to separate file
            income_categories = ['Зарплата', 'Вклады']
            expense_categories = ['Продукты', 'ЖКХ', 'Лекарства', 'Отдых']

            await orm_add_default_categories(session,
                                             telegram_id=telegram_id,
                                             income_categories=income_categories,
                                             expense_categories=expense_categories)
            return True

        except SQLAlchemyError as e:
            logger.error(f'Error when adding a new user to Users: {e}')

    logger.debug(f'User with telegram_id={telegram_id} already exists in Users')
    return False


async def orm_get_user_categories(
        session: AsyncSession,
        telegram_id: int,
        is_income: bool = False
) -> dict[str, int]:
    """Returns dictionary with names and ids of income or expense categories (in the form 'name: id') of user with specified telegram_id. If is_income is True, returns income categories, otherwise - expense categories"""

    user_id = await orm_get_user_id(session, telegram_id)
    table = CategoryIncome if is_income else CategoryExpense
    query = select(table).where(table.user_id == user_id and table.is_active == True)
    result = await session.execute(query)
    categories_scalars = result.scalars().all()
    categories = {category.name: category.id for category in categories_scalars}
    return categories


async def orm_add_income_expense(
        session: AsyncSession,
        *,
        telegram_id: int,
        is_income: bool = False,
        amount: float,
        category: str,
        description: Optional[str] = None,
        date_time: datetime,
):
    """Adds new income or expense to user with specified telegram_id"""

    user_id = await orm_get_user_id(session, telegram_id)
    categories = await orm_get_user_categories(session, telegram_id, is_income=is_income)
    category_id = categories[category]
    table_to_add = Income if is_income else Expense

    session.add(table_to_add(
        amount=amount,
        description=description,
        created=date_time,
        user_id=user_id,
        category_id=category_id,
    ))
    await session.commit()
