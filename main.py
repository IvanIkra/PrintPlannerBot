import asyncio
import logging
from datetime import date

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, Message, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config_reader import config
from db_manage import *
from payment import *

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
db_file = 'printbot.db'
conn = create_connection(db_file)
create_table(conn)  # Создание таблицы материалов, если ещё не создана
create_orders_table(conn)  # Создание таблицы заказов
create_revenue_table(conn)  # Создание таблицы доходов
create_expenses_table(conn)  # Создание таблицы расходов

keyboard1 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⛑️Помощь")]],
                                resize_keyboard=True,
                                input_field_placeholder="Выберете пункт меню")  # Создание блок-клавиатуры


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Вас приветствует команда разработчиков Binary Brigade. "
        "\nОтпратьте команду ⛑️Помощь, чтобы узнать список доступных команд", reply_markup=keyboard1)


@dp.message(lambda message: message.text in ["⛑️Помощь"])
async def cmd_help(message: types.Message):
    await message.answer("/help - узнать список доступных команд\n\n"
                         "/newoder <имя заказа>@<ссылка на файл>@<название материала>@<количество материала в граммах>@<дата выполнения>@<степень важности от 1 до 10>@<настройки> - новый заказ\n"
                         "Пример: /newoder Заказ 1@https://github.com/IvanIkra/PrintPlannerBot@ПЛА@100@16-01-2025@10@стандартные\n\n"
                         "/matupdateadd <название материала>@<количество материала> - добавить материал\n\n"
                         "/matupdatesub <название материала>@<количество материала> - использовать материал\n\n"
                         "/addexp <категория>@<сумма>@<название> - добавить расход\n\n"
                         "/getmats - выводит список всех материалов\n\n"
                         "/oder <id> - информация о закакзе по его id\n\n"
                         "/paymenturl <сумма> - создает платежную ссылку")


@dp.message(Command("newoder"))
async def cmd_newoder(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        name, link, matrial, material_amount, recommended_date, importance, settings = command.args.split("@")
        importance = int(importance)
        material_amount = int(material_amount)
        cost = material_amount * 7
    except Exception as e:
        await message.answer(
            "Ошибка: неправильный формат данных. Правильный формат:\n"
            "/newoder <имя заказа>@<ссылка на файл>@<название материала>@<количество материала>@<дата выполнения>@<степень важности от 1 до 10>@<настройки>"
        )
        print(e)
        return
    mat = update_material(conn, matrial, material_amount, 'subtract')
    if mat == 'Ошибка: недостаточно материала для вычитания.':
        await message.answer(mat)
        return
    id = add_order(conn, name, link, matrial, material_amount, recommended_date, importance, settings, cost, True,
                   False, date.today())
    add_revenue(conn, name, material_amount, date.today())

    await message.answer(id + f'\nЦена заказа: {cost}' + f'\n{mat}')


@dp.message(Command("matupdateadd"))
async def cmd_matupdateadd(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        material, material_amount = command.args.split("@")
        material_amount = int(material_amount)
    except Exception as e:
        await message.answer(
            "Ошибка: неправильный формат данных. Правильный формат:\n"
            "/matupdateadd <название материала>@<количество материала>"
        )
        print(e)
        return

    await message.answer(update_material(conn, material, material_amount, 'add'))


@dp.message(Command("matupdatesub"))
async def cmd_matupdatesub(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        material, material_amount = command.args.split("@")
        material_amount = int(material_amount)
    except Exception as e:
        await message.answer(
            "Ошибкwа: неправильный формат данных. Правильный формат:\n"
            "/matupdatesub <название материала>@<количество материала>"
        )
        print(e)
        return

    await message.answer(update_material(conn, material, material_amount, 'subtract'))


@dp.message(Command("addexp"))
async def cmd_addexp(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        name, summ, text = command.args.split("@")
        summ = int(summ)
    except Exception as e:
        await message.answer(
            "Ошибкwа: неправильный формат данных. Правильный формат:\n"
            "/addexp <категория>@<сумма>@<название>"
        )
        print(e)
        return

    await message.answer(add_expense(conn, name, summ, date.today(), text))


@dp.message(Command("getmats"))
async def cmd_getmats(message: types.Message):
    text = ''
    materials = get_all_materials(conn)
    text += "Список всех материалов:\n"
    for material in materials:
        text += f"Материал: {material[0]}, Количество: {material[1]} грамм\n"
    await message.answer(text)


@dp.message(Command("oder"))
async def cmd_oder(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        id = command.args
        id = int(id)
    except Exception as e:
        await message.answer(
            "Ошибкwа: неправильный формат данных. Правильный формат:\n"
            "/oder <id>"
        )
        print(e)
        return
    text = 'Данные заказа '
    for i in get_order_by_id(conn, id):
        text += str(i) + ' @ '
    await message.answer(text[:-3])


@dp.message(Command("paymenturl"))
async def cmd_url(
        message: Message,
        command: CommandObject
):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        summ = command.args
        summ = int(summ)
    except Exception as e:
        await message.answer(
            "Ошибкwа: неправильный формат данных. Правильный формат:\n"
            "/paymenturl <сумма>"
        )
        print(e)
        return
    await message.answer(generate_link(summ)[0])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
