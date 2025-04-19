import asyncio
import logging
import os
import tempfile
from datetime import date, datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, Message, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

import pandas as pd

import src.root.keyboards as kb
from src.root.fsm_order import (
    Ord, ord_1, ord_2, ord_3, ord_4, ord_5, ord_6, ord_7, ord_8, 
    get_order_data, create_order_in_db  # Добавляем create_order_in_db в импорт
)

from data.config_reader import config
from data.db_manage import *
from data.db_manage import DatabaseManager


log_file = 'data/logs/bot.log'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write('')

log_dir = os.path.join('data', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'bot.log')
with open(log_file, 'w', encoding='utf-8') as f:
    f.write('')

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler(log_file, encoding='utf-8'),
                           logging.StreamHandler()])

data_dir = os.path.join('data')
db_dir = os.path.join(data_dir, 'db')

os.makedirs(db_dir, exist_ok=True)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


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


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        image = types.FSInputFile("data/images/printplanner.webp")
        await message.answer_photo(
            photo=image,
            caption="👋 Вас приветствует команда разработчиков Binary Brigade."
        )
    except FileNotFoundError:
        await message.answer(
            "👋 Вас приветствует команда разработчиков Binary Brigade."
        )
    await message.answer(
        "*↓Нажмите, чтобы вызвать меню↓*",
        reply_markup=kb.keyboard_inline2,
        parse_mode="Markdown"
    )

@dp.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer('Добро пожаловать в меню бота-помощника в 3D печати!\
 Выберите нужный вам пункт меню.', reply_markup=kb.keyboard_inline_main_menu)

@dp.callback_query(F.data == 'make_order')
async def make_order(callback: CallbackQuery, state: FSMContext):
    # Удаляем сообщение с файлом, если оно есть
    await callback.message.delete()
    # Запускаем FSM
    await ord_1(callback, state)

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

@dp.callback_query(F.data == 'yes_makeorder')
async def yes_makeorder(callback: CallbackQuery, state: FSMContext):
    data = await get_order_data(state)
    
    # Расчет рекомендуемой стоимости
    recommended_cost = data["material_amount"] * 7  # 7 рублей за грамм
    
    # Сохраняем все данные заказа и рекомендуемую стоимость в состоянии
    await state.update_data(order_data=data, recommended_cost=recommended_cost)
    
    await callback.answer("Продолжение создания заказа")
    await callback.message.edit_text(
        f'Мы рекомендуем установить стоимость *{recommended_cost}* руб',
        reply_markup=kb.keyboard_inline8,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == 'our_price_makeorder')
async def our_price_makeorder(callback: CallbackQuery, state: FSMContext):
    try:
        # Получаем данные из состояния
        state_data = await state.get_data()
        data = state_data["order_data"]
        recommended_cost = state_data["recommended_cost"]
        
        # Создаем заказ с рекомендуемой стоимостью
        user_id = callback.from_user.id
        data["cost"] = recommended_cost
        order_id = await create_order_in_db(user_id, data)
        
        if order_id == -1:
            await callback.answer("Произошла ошибка при создании заказа")
            await callback.message.edit_text(
                "Ошибка при создании заказа. Попробуйте еще раз.",
                reply_markup=kb.keyboard_inline7
            )
            return
        
        await callback.answer("Готово")
        await callback.message.edit_text(
            f'Заказ *{data["name"]}* создан!\nID заказа: *{order_id}*\nСтоимость: *{recommended_cost}* руб',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.backmenu_button]]),
            parse_mode="Markdown"
        )
        await state.clear()
        
    except Exception as e:
        print(f"Error in our_price_makeorder: {e}")
        await callback.message.edit_text(
            "Произошла ошибка при создании заказа",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.backmenu_button]])
        )

@dp.message(Payment.summ)
async def handle_custom_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        user_id = message.from_user.id
        
        # Получаем данные заказа из состояния
        state_data = await state.get_data()
        data = state_data["order_data"]
        
        # Создаем заказ с пользовательской стоимостью
        data["cost"] = price
        order_id = await create_order_in_db(user_id, data)
        
        if order_id == -1:
            await message.answer(
                "Произошла ошибка при создании заказа",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.backmenu_button]])
            )
            await state.clear()
            return
        
        await state.clear()
        await message.answer(
            f'Заказ *{data["name"]}* создан!\nID заказа: *{order_id}*\nСтоимость: *{price}* руб',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.backmenu_button]]),
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.cancel_button]])
        )

@dp.callback_query(F.data == 'custom_price_makeorder')
async def custom_price_makeorder(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Переход к вводу стоимости")
    await state.set_state(Payment.summ)
    await callback.message.edit_text(
        "Введите стоимость:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.cancel_button]])
    )

@dp.callback_query(F.data == "cancel_price")
async def cancel_price(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Установка стоимости отменена. Вы можете вернуться к меню",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kb.backmenu_button]])
    )

# @dp.message(Command("help"))
# async def cmd_help(message: types.Message):
#     await message.answer("/help - узнать список доступных команд\n\n"
#                          "/newoder <имя заказа>@<ссылка на файл>@<название материала>@<количество материала\
#                          в граммах>@<дата выполнения>@<степень важности от 1 до 10>@<настройки> - новый заказ\n"
#                          "Пример: /newoder Заказ 1@https://github.com/IvanIkra/PrintPlannerBot@ПЛА\
#                          @100@16-01-2025@10@стандартные\n\n"
#                          "/matupdateadd <название материала>@<количество материала> - добавить материал\n\n"
#                          "/matupdatesub <название материала>@<количество материала> - использовать материал\n\n"
#                          "/addexp <категория>@<сумма>@<название> - добавить расход\n\n"
#                          "/getmats - выводит список всех материалов\n\n"
#                          "/oder <id> - информация о закакзе по его id\n\n"
#                          "/paymenturl <сумма> - создает платежную ссылку")
#
#
# @dp.message(Command("newoder"))
# async def cmd_newoder(
#         message: Message,
#         command: CommandObject
# ):
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     try:
#         name, link, matrial, material_amount, recommended_date, importance, settings = command.args.split("@")
#         importance = int(importance)
#         material_amount = int(material_amount)
#         cost = material_amount * 7
#     except Exception as e:
#         await message.answer(
#             "Ошибка: неправильный формат данных. Правильный формат:\n"
#             "/newoder <имя заказа>@<ссылка на файл>@<название материала>\
#             @<количество материала>@<дата выполнения>@<степень важности от 1 до 10>@<настройки>"
#         )
#         print(e)
#         return
#     mat = update_material(conn, matrial, material_amount, 'subtract')
#     if mat == 'Ошибка: недостаточно материала для вычитания.':
#         await message.answer(mat)
#         return
#     id = add_order(conn, name, link, matrial, material_amount, recommended_date, importance, settings, cost, True,
#                    False, date.today())
#     add_revenue(conn, name, material_amount, date.today())
#
#     await message.answer(id + f'\nЦена заказа: {cost}' + f'\n{mat}')
#
#
# @dp.message(Command("matupdateadd"))
# async def cmd_matupdateadd(
#         message: Message,
#         command: CommandObject
# ):
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     try:
#         material, material_amount = command.args.split("@")
#         material_amount = int(material_amount)
#     except Exception as e:
#         await message.answer(
#             "Ошибка: неправильный формат данных. Правильный формат:\n"
#             "/matupdateadd <название материала>@<количество материала>"
#         )
#         print(e)
#         return
#
#     await message.answer(update_material(conn, material, material_amount, 'add'))
#
#
# @dp.message(Command("matupdatesub"))
# async def cmd_matupdatesub(
#         message: Message,
#         command: CommandObject
# ):
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     try:
#         material, material_amount = command.args.split("@")
#         material_amount = int(material_amount)
#     except Exception as e:
#         await message.answer(
#             "Ошибка: неправильный формат данных. Правильный формат:\n"
#             "/matupdatesub <название материала>@<количество материала>"
#         )
#         print(e)
#         return
#
#     await message.answer(update_material(conn, material, material_amount, 'subtract'))
#
#
# @dp.message(Command("addexp"))
# async def cmd_addexp(
#         message: Message,
#         command: CommandObject
# ):
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     try:
#         name, summ, text = command.args.split("@")
#         summ = int(summ)
#     except Exception as e:
#         await message.answer(
#             "Ошибка: неправильный формат данных. Правильный формат:\n"
#             "/addexp <категория>@<сумма>@<название>"
#         )
#         print(e)
#         return
#
#     await message.answer(add_expense(conn, name, summ, date.today(), text))
#
#
# @dp.message(Command("getmats"))
# async def cmd_getmats(message: types.Message):
#     text = ''
#     materials = get_all_materials(conn)
#     text += "Список всех материалов:\n"
#     for material in materials:
#         text += f"Материал: {material[0]}, Количество: {material[1]} грамм\n"
#     await message.answer(text)
#
#
# @dp.message(Command("oder"))
# async def cmd_oder(
#         message: Message,
#         command: CommandObject
# ):
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     try:
#         id = command.args
#         id = int(id)
#     except Exception as e:
#         await message.answer(
#             "Ошибка: неправильный формат данных. Правильный формат:\n"
#             "/oder <id>"
#         )
#         print(e)
#         return
#     text = 'Данные заказа '
#     for i in get_order_by_id(conn, id):
#         text += str(i) + ' @ '
#     await message.answer(text[:-3])
#
#
# @dp.message(Command("paymenturl"))
# async def cmd_url(
#         message: Message,
#         command: CommandObject
# ):
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     try:
#         summ = command.args
#         summ = int(summ)
#     except Exception as e:
#         await message.answer(
#             "Ошибка: неправильный формат данных. Правильный формат:\n"
#             "/paymenturl <сумма>"
#         )
#         print(e)
#         return
#     await message.answer(generate_link(summ)[0])

@dp.callback_query(F.data == "back_universal")
async def universal_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    
    state_transitions = {
        Ord.link: (Ord.name, "Введите название заказа"),
        Ord.material: (Ord.link, "Введите ссылку на 3D модель"),
        Ord.material_amount: (Ord.material, "Введите название используемого материала"),
        Ord.recommended_date: (Ord.material_amount, "Введите количество(в граммах) используемого материала (целое число)"),
        Ord.importance: (Ord.recommended_date, "Введите дату выполнения (в формате ГГГГ-ММ-ДД)"),
        Ord.settings: (Ord.importance, "Введите важность заказа от 1 до 10 (целое число)")
    }

    if current_state == Ord.name:
        await callback.answer("Вы вернулись назад")
        await callback.message.edit_text(
            'Ваши не выполненные заказы:',
            reply_markup=kb.keyboard_inline1
        )
        await state.clear()
    elif current_state in state_transitions:
        prev_state, message_text = state_transitions[current_state]
        data = await state.get_data()
        await state.set_state(prev_state)
        await state.update_data(**data)
        await callback.answer("Вы вернулись назад")
        await callback.message.edit_text(
            message_text,
            reply_markup=kb.keyboard_inline6
        )
    else:
        await callback.answer("Вы вернулись в главное меню")
        await callback.message.edit_text(
            'Добро пожаловать в меню бота-помощника в 3D печати! Выберите нужный вам пункт меню.',
            reply_markup=kb.keyboard_inline_main_menu
        )
        if current_state is not None:
            await state.clear()

@dp.callback_query(F.data == 'menus')
async def make_order(callback: CallbackQuery):
    await callback.answer("Вы перешли к меню")
    await callback.message.edit_text(
        'Добро пожаловать в меню бота-помощника в 3D печати! Выберите нужный вам пункт меню.',
        reply_markup=kb.keyboard_inline_main_menu
    )

@dp.callback_query(F.data == 'cancel_order')
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Отмена создания заказа")
    await callback.message.delete()
    
    try:
        user_id = callback.from_user.id
        db_manager = DatabaseManager(f'data/db/user{user_id}data.db')
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            excel_path = tmp.name
            has_orders = db_manager.export_pending_orders_to_excel(excel_path)
            db_manager.close_connection()

        if has_orders:
            excel_file = types.FSInputFile(excel_path, filename="Невыполненные заказы.xlsx")
            await callback.message.answer_document(
                document=excel_file,
                caption="Выберите действие:",
                reply_markup=kb.keyboard_inline1
            )
        else:
            await callback.message.answer(
                'У вас нет невыполненных заказов.',
                reply_markup=kb.keyboard_inline1
            )
        
        os.unlink(excel_path)
            
    except Exception as e:
        print(f"Error in cancel_order: {e}")
        await callback.message.answer(
            'Произошла ошибка при получении списка заказов.',
            reply_markup=kb.keyboard_inline1
        )
    
    await state.clear()

@dp.callback_query(F.data == 'order_manage')
async def make_order(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        db_manager = DatabaseManager(f'data/db/user{user_id}data.db')
        
        # Используем временный файл
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            excel_path = tmp.name
            has_orders = db_manager.export_pending_orders_to_excel(excel_path)
            db_manager.close_connection()

        # Удаляем старое сообщение
        await callback.message.delete()

        if has_orders:
            excel_file = types.FSInputFile(excel_path, filename="Невыполненные заказы.xlsx")
            await callback.message.answer_document(
                document=excel_file,
                caption="Выберите действие:",
                reply_markup=kb.keyboard_inline1
            )
        else:
            await callback.message.answer(
                'У вас нет невыполненных заказов.',
                reply_markup=kb.keyboard_inline1
            )
        
        # Удаляем временный файл
        os.unlink(excel_path)
            
    except Exception as e:
        print(f"Error in order_manage: {e}")
        await callback.message.answer(
            'Произошла ошибка при получении списка заказов.',
            reply_markup=kb.keyboard_inline1
        )

@dp.callback_query(F.data == 'back_menu')
async def back_to_menu(callback: CallbackQuery):  # Изменено имя функции, чтобы избежать конфликтов
    await callback.answer("Вы перешли к меню")
    try:
        # Пробуем отредактировать сообщение
        await callback.message.edit_text(
            'Добро пожаловать в меню бота-помощника в 3D печати! Выберите нужный вам пункт меню.',
            reply_markup=kb.keyboard_inline_main_menu
        )
    except TelegramBadRequest as e:
        if "there is no text in the message to edit" in str(e):
            # Это ожидаемое поведение для сообщений с файлом
            await callback.message.delete()
            await callback.message.answer(
                'Добро пожаловать в меню бота-помощника в 3D печати! Выберите нужный вам пункт меню.',
                reply_markup=kb.keyboard_inline_main_menu
            )
        else:
            # Логируем только неожиданные ошибки
            print(f"Unexpected error in back_to_menu: {e}")

@dp.callback_query(F.data == 'material_manage')
async def make_order(callback: CallbackQuery):
    await callback.answer("Вы перешли к панели управления материалами")
    await callback.message.edit_text(
        'Материалы в наличии:',
        reply_markup=kb.keyboard_inline3
    )

@dp.callback_query(F.data == 'finance_manage')
async def make_order(callback: CallbackQuery):
    await callback.answer("Вы перешли к панели управления финансами")
    await callback.message.edit_text(
        'Финансы за последний месяц:',
        reply_markup=kb.keyboard_inline4
    )
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
