from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)

back_button = InlineKeyboardButton(text='⬅️ Назад', callback_data='back_universal')
cancel_button = InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_order')
backmenu_button = InlineKeyboardButton(text='💼Возврат к меню💼', callback_data='back_menu')

keyboard_inline1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Новый заказ', callback_data='make_order')],
        [InlineKeyboardButton(text='Заказ выполнен', callback_data='done_order')],
        [InlineKeyboardButton(text='Посмотреть выполненные заказы', callback_data='show_orders')],
        [InlineKeyboardButton(text='Удалить заказ', callback_data='delete_order')],
        [backmenu_button]
    ])

keyboard_inline2 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='💼Меню💼', callback_data='menus')]])

keyboard_inline_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Управление заказами', callback_data='order_manage'),
            InlineKeyboardButton(text='Управление материалами', callback_data='material_manage')],
        [InlineKeyboardButton(text='Создать платёжную ссылку', callback_data='make_paylink')],
        [InlineKeyboardButton(text='Управление финансами', callback_data='finance_manage')]
    ])

keyboard_inline3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить материал', callback_data='add_material')],
        [InlineKeyboardButton(text='Использовать материал', callback_data='use_material')],
        [backmenu_button]
                     ])

keyboard_inline4 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить доход', callback_data='add_income')],
        [InlineKeyboardButton(text='Добавить расход', callback_data='add_expense')],
        [InlineKeyboardButton(text='Финансы за промежуток времени', callback_data='finance_interval')],
        [backmenu_button]
                     ])

keyboard_inline5 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Да✅', callback_data='yes_makeorder'),
         InlineKeyboardButton(text='Нет❌', callback_data='cancel_order')]
                     ])

keyboard_inline6 = InlineKeyboardMarkup(
    inline_keyboard=[
        [back_button, cancel_button]
    ])

keyboard_inline7 = InlineKeyboardMarkup(
    inline_keyboard=[
        [backmenu_button]
    ])
keyboard_inline8 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Наша стоимость", callback_data="our_price_makeorder")],
    [InlineKeyboardButton(text="Своя стоимость", callback_data="custom_price_makeorder")],
    [cancel_button]  # Используем существующую кнопку отмены
])
