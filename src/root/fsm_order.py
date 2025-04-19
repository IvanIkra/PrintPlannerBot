from datetime import date

from aiogram import F, Dispatcher
from aiogram.filters.command import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import src.root.keyboards as kb
from data.db_manage import DatabaseManager

from datetime import datetime

__all__ = [
    'Ord', 'ord_1', 'ord_2', 'ord_3', 'ord_4', 'ord_5', 'ord_6', 'ord_7', 'ord_8',
    'get_order_data', 'create_order_in_db'
]


class Ord(StatesGroup):
    name = State()
    link = State()
    material = State()
    material_amount = State()
    recommended_date = State()
    importance = State()
    settings = State()


class Payment(StatesGroup):
    summ = State()


async def ord_1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Ord.name)
    # Вместо edit_text используем answer
    await callback.message.answer(
        "Введите название заказа",
        reply_markup=kb.keyboard_inline6
    )


async def ord_2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Ord.link)
    await message.answer("Введите ссылку на 3D модель",
                         reply_markup=kb.keyboard_inline6)


async def ord_3(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await state.set_state(Ord.material)
    await message.answer("Введите название используемого материала",
                         reply_markup=kb.keyboard_inline6)


async def ord_4(message: Message, state: FSMContext):
    await state.update_data(material=message.text)
    await state.set_state(Ord.material_amount)
    await message.answer("Введите количество(в граммах) используемого материала (целое число)",
                         reply_markup=kb.keyboard_inline6)


async def ord_5(message: Message, state: FSMContext):
    try:
        material_amount = int(message.text)
        await state.update_data(material_amount=material_amount)
        await state.set_state(Ord.recommended_date)
        await message.answer("Введите дату выполнения (в формате ГГГГ-ММ-ДД)",
                             reply_markup=kb.keyboard_inline6)
    except ValueError:
        await message.answer("Ошибка: количество материала должно быть целым числом. Пожалуйста, введите заново.",
                             reply_markup=kb.keyboard_inline6)


async def ord_6(message: Message, state: FSMContext):
    try:
        recommended_date = date.fromisoformat(message.text)
        await state.update_data(recommended_date=recommended_date)
        await state.set_state(Ord.importance)
        await message.answer("Введите важность заказа от 1 до 10 (целое число)",
                             reply_markup=kb.keyboard_inline6)
    except ValueError:
        await message.answer("Ошибка: дата должна быть в формате ГГГГ-ММ-ДД. Пожалуйста, введите заново.",
                             reply_markup=kb.keyboard_inline6)


async def ord_7(message: Message, state: FSMContext):
    try:
        importance = int(message.text)
        if 1 <= importance <= 10:
            await state.update_data(importance=importance)
            await state.set_state(Ord.settings)
            await message.answer("Введите необходимые настройки для печати",
                                 reply_markup=kb.keyboard_inline6)
        else:
            await message.answer("Ошибка: важность должна быть в диапазоне от 1 до 10. Пожалуйста, введите заново.",
                                 reply_markup=kb.keyboard_inline6)
    except ValueError:
        await message.answer("Ошибка: важность должна быть целым числом. Пожалуйста, введите заново.",
                             reply_markup=kb.keyboard_inline6)


async def ord_8(message: Message, state: FSMContext):
    await state.update_data(settings=message.text)
    data = await state.get_data()

    text = (
        f"Название: {data['name']}\n"
        f"Ссылка: {data['link']}\n"
        f"Материал: {data['material']}\n"
        f"Количество материала: {data['material_amount']}\n"
        f"Дата выполнения: {data['recommended_date']}\n"
        f"Важность: {data['importance']}\n"
        f"Настройки: {data['settings']}\n\n"
        f"Вы хотите продолжить создание заказа с этими данными?"
    )

    # Используем клавиатуру с кнопками да/нет
    await message.answer(text, reply_markup=kb.keyboard_inline5)


async def get_order_data(state: FSMContext):
    data = await state.get_data()
    await state.clear()
    return data


async def create_order_in_db(user_id: int, data: dict) -> int:
    try:
        db_manager = DatabaseManager(f'data/db/user{user_id}data.db')
        order_id = db_manager.add_order(
            name=data["name"],
            link=data["link"],
            material=data["material"],
            material_amount=data["material_amount"],
            recommended_date=data["recommended_date"],
            importance=data["importance"],
            settings=data["settings"],
            cost=data["cost"],  # Используем рассчитанную стоимость
            payment_info=False,
            done=False,
            creation_date=datetime.now().strftime('%Y-%m-%d')
        )
        db_manager.close_connection()
        return order_id
    except Exception as e:
        print(f"Error creating order in db: {e}")
        return -1


def handle_order_states(dp: Dispatcher) -> None:
    """Регистрирует все обработчики состояний заказа"""

    @dp.message(Ord.name)
    async def handle_name(message: Message, state: FSMContext):
        await ord_2(message, state)

    @dp.message(Ord.link)
    async def handle_link(message: Message, state: FSMContext):
        await ord_3(message, state)

    @dp.message(Ord.material)
    async def handle_material(message: Message, state: FSMContext):
        await ord_4(message, state)

    @dp.message(Ord.material_amount)
    async def handle_material_amount(message: Message, state: FSMContext):
        await ord_5(message, state)

    @dp.message(Ord.recommended_date)
    async def handle_date(message: Message, state: FSMContext):
        await ord_6(message, state)

    @dp.message(Ord.importance)
    async def handle_importance(message: Message, state: FSMContext):
        await ord_7(message, state)

    @dp.message(Ord.settings)
    async def handle_settings(message: Message, state: FSMContext):
        await ord_8(message, state)
