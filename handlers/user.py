import random
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from keyboards import keyboards
from database import database
from GigaQueryEngine import create_random_text, prompts_text


class UserStates(StatesGroup):
    waiting_for_query = State()


user_router = Router()


async def send_text(callback_or_message, state: FSMContext, theme_text=None, is_query=False):
    send_method = callback_or_message.message.answer if isinstance(callback_or_message,
                                                                   CallbackQuery) else callback_or_message.answer
    tg_id = callback_or_message.from_user.id if isinstance(callback_or_message,
                                                           CallbackQuery) else callback_or_message.from_user.id

    try:
        await database.process_user_query(tg_id)
    except Exception:
        await send_method(text='У вас закончились бесплатные генерации!')
        await state.clear()
        return

    text = create_random_text(theme_text, is_query)
    await state.update_data(text_type=theme_text)

    await send_method(text=f"{text}", reply_markup=keyboards.after_text())

    await state.clear()


@user_router.message(CommandStart())
@user_router.message(F.text == 'Главное меню')
async def start_menu(message: Message, state: FSMContext):
    await database.add_user(message.from_user.id)

    await message.answer(
        text=f'Привет, {message.from_user.first_name}! Я бот ГигаЧат, я могу генерировать текста.\nВыбери действие:',
        reply_markup=keyboards.start_menu())
    await state.clear()


@user_router.callback_query(F.data == 'generate_random_text')
async def text_random(callback: CallbackQuery, state: FSMContext):
    prompt_text = random.choice(list(prompts_text.keys()))
    await send_text(callback, state, theme_text=prompt_text)


@user_router.callback_query(F.data == 'generate_text_on_query')
async def ask_for_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите желаемый запрос:")
    await state.set_state(UserStates.waiting_for_query)


@user_router.message(UserStates.waiting_for_query)
async def generate_text_from_query(message: Message, state: FSMContext):
    user_query = message.text

    try:
        await database.process_user_query(message.from_user.id)
    except Exception:
        await message.answer(
            text='У вас закончились бесплатные генерации!')
        await state.clear()
        return

    story = create_random_text(user_query, is_query=True)
    await message.answer(f"Вот ваш текст:\n{story}", reply_markup=keyboards.after_text())

    await state.clear()


@user_router.callback_query(F.data == 'personal_cabinet')
async def user_info(callback: CallbackQuery):
    user_info = await database.get_user_data(callback.from_user.id)
    text = f'Информация о пользователе:\nusername: @{callback.from_user.username}\nОсталось запросов: {user_info[1]} из 20'
    await callback.message.answer(text=text)
