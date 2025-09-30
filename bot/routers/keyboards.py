from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Редактировать",
                callback_data="edit"
            )
        ],
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data="confirm"
            )
        ],
        [
            InlineKeyboardButton(
                text="Отменить",
                callback_data="reject"
            )
        ]
    ]
)

edit_choose_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Наименование объекта',
                callback_data='name',
            )
        ],
        [
            InlineKeyboardButton(
                text='Наименование, ИНН конечного заказчика',
                callback_data='inn_name_customer',
            )
        ],
        [
            InlineKeyboardButton(
                text='Адрес объекта',
                callback_data='adress',
            )
        ],
        [
            InlineKeyboardButton(
                text='Тип',
                callback_data='type',
            )
        ],
        [
            InlineKeyboardButton(
                text='Ген. Подрядчик. Наименование, ИНН',
                callback_data='inn_name_gen_contr',
            )
        ],
        [
            InlineKeyboardButton(
                text='Субподрядчик. Наименование, ИНН',
                callback_data='inn_name_subcontr',
            )
        ],
        [
            InlineKeyboardButton(
                text='Монтажник/закупщик. Наименование, ИНН',
                callback_data='inn_name_buyer',
            )
        ],
        [
            InlineKeyboardButton(
                text='Проектировщик. Наименование, ИНН',
                callback_data='inn_name_designer',
            )
        ],
        [
            InlineKeyboardButton(
                text='Тип закупки (прямая/тендер)',
                callback_data='purchase_type',
            )
        ],
        [
            InlineKeyboardButton(
                text='Номер бланка регистрации объекта (по\nномеру КП)',
                callback_data='blank_num',
            )
        ],
        [
            InlineKeyboardButton(
                text='Дата регистрации объекта',
                callback_data='reg_date',
            )
        ],
        [
            InlineKeyboardButton(
                text='Персональный менеджер',
                callback_data='manager',
            )
        ],
        [
            InlineKeyboardButton(
                text='Телефон',
                callback_data='phone',
            )
        ],
        [
            InlineKeyboardButton(
                text='Почта',
                callback_data='email',
            )
        ]
    ]
)

check_continue_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Продолжить заполнение",
                callback_data="continue"
            )
        ],
        [
            InlineKeyboardButton(
                text="Отменить",
                callback_data="reject"
            )
        ]
    ]
)
