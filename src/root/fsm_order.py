from datetime import date

from aiogram import F
from aiogram.filters.command import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

import src.root.keyboards as kb


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
    await callback.answer("Переход к созданию заказа")
    await callback.message.edit_text("Введите название заказа",
                                   reply_markup=kb.keyboard_inline6)
    await state.set_state(Ord.name)


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
    await message.answer(
        f'Имя заказа: {data["name"]}\n'
        f'Ссылка на 3D модель: {data["link"]}\n'
        f'Материал: {data["material"]}\n'
        f'Количество материала: {data["material_amount"]}\n'
        f'Дата выполнения: {data["recommended_date"]}\n'
        f'Важность: {data["importance"]}\nНастройки: {data["settings"]}'
        f'\n\n*Вы хотите создать заказ с этими данными?*', reply_markup=kb.keyboard_inline5, parse_mode="Markdown")
    
    
async def get_order_data(state: FSMContext):
    data = await state.get_data()
    await state.clear()
    return data