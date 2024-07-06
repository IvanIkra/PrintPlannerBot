from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

keyboard_reply = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Меню")]])

keyboard_inline1 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Создать заказ', callback_data='make_order')]])
keyboard_inline2 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='💼Меню💼', callback_data='menus')]])
