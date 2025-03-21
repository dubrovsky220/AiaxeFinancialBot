############# Finite state machine for adding new income or expense #############
from datetime import datetime
from typing import Optional

from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_user_categories, orm_add_income_expense
from handlers.menu_processing import get_main_page
from keyboards.inline import MenuCallBack, get_cancel_button, get_category_list_buttons, get_skip_buttons, \
    get_save_buttons, get_main_menu_buttons

state_machines_router = Router()


######### Finite state machine for adding new income or expense ###########

class AddIncomeExpense(StatesGroup):
    amount = State()
    category = State()
    description = State()

    is_income: Optional[bool] = None
    previous_bot_message_id: Optional[int] = None


@state_machines_router.callback_query(
    StateFilter(None),
    MenuCallBack.filter(F.menu_name.in_(['add_expense', 'add_income']))
)
async def add_income_expense_callback(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        state: FSMContext,
):
    """Handles clicks on inline menu buttons 'Добавить расход' and 'Добавить доход'"""

    if callback_data.menu_name == 'add_expense':
        await callback.message.edit_text(text='Введите сумму расхода: ', reply_markup=get_cancel_button())
        AddIncomeExpense.is_income = False
    elif callback_data.menu_name == 'add_income':
        await callback.message.edit_text(text='Введите сумму дохода: ', reply_markup=get_cancel_button())
        AddIncomeExpense.is_income = True

    AddIncomeExpense.previous_bot_message_id = callback.message.message_id
    await state.set_state(AddIncomeExpense.amount)


@state_machines_router.message(AddIncomeExpense.amount)
async def add_income_expense_amount(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.delete_message(message.chat.id, AddIncomeExpense.previous_bot_message_id)
    text = message.text
    number_parts = text.split('.')
    await message.delete()

    if (
            len(number_parts) > 2
            or (len(number_parts) == 1 and not number_parts[0].isdigit())
            or (len(number_parts) == 2 and not (number_parts[0].isdigit() and number_parts[1].isdigit()))
    ):
        sent_message = await message.answer(
            '<b>Вводить можно только положительное десятичное число, разделённое точкой!</b>\n\nВведите сумму корректно:',
            reply_markup=get_cancel_button())
    elif len(number_parts[0]) > 10:
        sent_message = await message.answer(
            '<b>Длина целой части числа не должна превышать 10 цифр!</b>\n\nВведите сумму корректно:',
            reply_markup=get_cancel_button())
    else:
        categories = await orm_get_user_categories(
            session,
            telegram_id=message.from_user.id,
            is_income=AddIncomeExpense.is_income
        )
        category_names = list(categories.keys())

        sizes = tuple([2 for _ in range(len(category_names) // 2)] + [1])

        keyboard = get_category_list_buttons(
            categories=category_names,
            level=1,
            menu_name=['add_expense', 'add_income'][AddIncomeExpense.is_income],
            create_add_button=False,
            sizes=sizes,
        )
        sent_message = await message.answer(
            f'Выберите категорию {"дохода" if AddIncomeExpense.is_income else "расхода"}:',
            reply_markup=keyboard)

        amount = round(float(text), 2)
        await state.update_data(amount=amount)
        await state.set_state(AddIncomeExpense.category)

    AddIncomeExpense.previous_bot_message_id = sent_message.message_id


@state_machines_router.callback_query(AddIncomeExpense.category, MenuCallBack.filter(F.level != 0))
async def add_income_expense_category(callback: CallbackQuery, callback_data: MenuCallBack, state: FSMContext):
    await state.update_data(category=callback_data.category)
    await callback.message.edit_text('Введите примечание к операции или нажмите кнопку "Пропустить":',
                                     reply_markup=get_skip_buttons())
    await state.set_state(AddIncomeExpense.description)
    AddIncomeExpense.previous_bot_message_id = callback.message.message_id
    await callback.answer()


@state_machines_router.callback_query(AddIncomeExpense.description, MenuCallBack.filter(F.action == 'skip'))
async def skip_income_expense_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    state_data = await state.get_data()
    message_text = f'{["➖", "➕"][AddIncomeExpense.is_income]} {state_data["amount"]:.2f} - {state_data["category"]}'
    await callback.message.edit_text(message_text, reply_markup=get_save_buttons())
    AddIncomeExpense.previous_bot_message_id = callback.message.message_id
    await callback.answer()


@state_machines_router.message(AddIncomeExpense.description)
async def add_income_expense_description(message: Message, state: FSMContext, bot: Bot):
    await bot.delete_message(message.chat.id, AddIncomeExpense.previous_bot_message_id)
    text = message.text
    await message.delete()

    if len(text) > 150:
        await message.answer(
            '<b>Длина примечания не должна превышать 150 символов!</b>\n\nВведите примечание корректно:',
            reply_markup=get_skip_buttons())
    else:
        await state.update_data(description=text)
        state_data = await state.get_data()
        message_text = f'{["➖", "➕"][AddIncomeExpense.is_income]} {state_data["amount"]:.2f} - {state_data["category"]} - {state_data["description"]}'
        await message.answer(message_text, reply_markup=get_save_buttons())


@state_machines_router.callback_query(AddIncomeExpense.description, MenuCallBack.filter(F.action == 'save'))
async def save_income_expense(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    date_time = datetime.now()

    try:
        await orm_add_income_expense(
            session,
            telegram_id=callback.from_user.id,
            is_income=AddIncomeExpense.is_income,
            amount=state_data["amount"],
            category=state_data["category"],
            description=state_data["description"],
            date_time=date_time,
        )
        logger.debug(f'Added new income/expense for user with telegram_id = {callback.message.from_user.id}')
        await callback.answer('Запись добавлена успешно!')

    except SQLAlchemyError as e:
        logger.error(f'Error when adding income or expense: {e}')
        await callback.answer('При добавлении записи произошла ошибка! Попробуйте еще раз.', show_alert=True)

    AddIncomeExpense.is_income = None
    await state.clear()
    text, keyboard_markup = get_main_page(session, level=0, menu_name='main')
    await callback.message.edit_text(text=text, reply_markup=keyboard_markup)
