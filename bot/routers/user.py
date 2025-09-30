from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, BotCommandScopeChat
from utils.documents import extract_table_from_blank
from routers.keyboards import main_keyboard, edit_choose_keyboard, check_continue_keyboard
from utils.utils import make_reply, check_adress_exist, check_inn_exist, check_name_exist
from routers.commands import user_commands, admin_commands
from routers.states import UserForm, EditForm
from typing import Optional
from config import Settings
from pathlib import Path
from db import Db
import logging
import asyncio


router = Router()


@router.message(StateFilter(EditForm.analyze, EditForm.edit))
async def analyze_message(message: Message):
    await message.answer("Сначала закончите добавление предыдущего объекта")


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    role = await Db.get_user_role(message.from_user.id)
    if role in {"user", "admin"}:
        welcome_message = """👋 Приветствую, я бот для сохранения объектов в базу данных.
Чтобы добавить новый объект, введите команду /form или отправьте бланк в 'pdf' формате.
Для помощи введите команду /help"""
        if role == 'admin':
            commands = admin_commands
            welcome_message += """\nТак как вы являетесь админов, вам доступен ряд дополнительных команд, подробнее в команде /help"""
        else:
            commands = user_commands
        await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=message.from_user.id))
        await message.answer(welcome_message)
    else:
        await bot.set_my_commands(commands=[], scope=BotCommandScopeChat(chat_id=message.from_user.id))
        await message.answer(
            "👋 Приветствую, к сожалению, у вас нет доступа к данному боту. Обратитесь к администратору"
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    role = await Db.get_user_role(message.from_user.id)
    help_message = (
        "Доступные команды:\n"
        "/start - приветствие\n"
        "/help - это сообщение\n"
        "/form - ввести данные объекта вручную. Если данные свопадут с уже существующим "
        "объектом, то объект не будет добален в базу, вам выведется существующий объект"
    )
    if role == 'admin':
        help_message += (
            "\n"
            "/search - поиск объекта в базе. Введите частично или полностью название объекта, "
            "адрес объекта, ИНН или название подрядчика\n"
            "/delete - удалить объект по id. id можо взять из результата /search\n"
            "/promote - присвоить пользователю статус админа по id\n"
            "/grant - предоставить пользователю доступ по его id\n"
            "/ban - запретить пользователю доступ по его id"
        )
    await message.answer(help_message)


@router.message(Command("form"))
async def cmd_form(message: Message, state: FSMContext):
    await state.set_state(UserForm.object_name)
    await message.answer("Наименование объекта")


@router.message(UserForm.object_name)
async def form_object_name(message: Message, state: FSMContext):
    flag, obj, service = await check_name_exist(message.text)
    if flag:
        reply_text = make_reply(dict(obj))
        await state.set_state(UserForm.check_continue)
        await state.update_data(
            name=message.text,
            name_service=service,
            continue_state=UserForm.inn_name_customer,
            continue_text="Наименование, ИНН конечного заказчика"
        )
        await message.answer("Данный объект уже добавлен в базу\n\n")
        await asyncio.sleep(2)
        await message.answer(reply_text, reply_markup=check_continue_keyboard)
        return
    await state.update_data(
        name=message.text,
        name_service=service,
    )
    await state.set_state(UserForm.inn_name_customer)
    await message.answer("Наименование, ИНН конечного заказчика")


@router.message(UserForm.inn_name_customer)
async def form_inn_name_customer(message: Message, state: FSMContext):
    flag, obj, service = await check_inn_exist(message.text)
    if flag:
        reply_text = make_reply(dict(obj))
        await state.set_state(UserForm.check_continue)
        await state.update_data(
            inn_name_customer=message.text,
            inn_name_customer_service=service,
            continue_state=UserForm.adress,
            continue_text="Адрес объекта"
        )
        await message.answer("Данный объект уже добавлен в базу\n\n")
        await asyncio.sleep(2)
        await message.answer(reply_text, reply_markup=check_continue_keyboard)
        return
    await state.update_data(
        inn_name_customer=message.text,
        inn_name_customer_service=service
    )
    await state.set_state(UserForm.adress)
    await message.answer("Адрес объекта")


@router.message(UserForm.adress)
async def form_adress(message: Message, state: FSMContext):
    flag, obj, service = await check_adress_exist(message.text)
    if flag:
        reply_text = make_reply(dict(obj))
        await state.set_state(UserForm.check_continue)
        await state.update_data(
            adress=message.text,
            adress_service=service,
            continue_state=UserForm.type,
            continue_text="Тип"
        )
        await message.answer("Данный объект уже добавлен в базу\n\n")
        await asyncio.sleep(2)
        await message.answer(reply_text, reply_markup=check_continue_keyboard)
        return
    await state.update_data(
        adress=message.text,
        adress_service=service
    )
    await state.set_state(UserForm.type)
    await message.answer("Тип")


@router.message(UserForm.type)
async def form_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(UserForm.inn_name_gen_contr)
    await message.answer("Ген. Подрядчик. Наименование, ИНН")


@router.message(UserForm.inn_name_gen_contr)
async def form_inn_name_gen_contr(message: Message, state: FSMContext):
    await state.update_data(inn_name_gen_contr=message.text)
    await state.set_state(UserForm.inn_name_subcontr)
    await message.answer("Субподрядчик. Наименование, ИНН")


@router.message(UserForm.inn_name_subcontr)
async def form_inn_name_subcontr(message: Message, state: FSMContext):
    await state.update_data(inn_name_subcontr=message.text)
    await state.set_state(UserForm.inn_name_buyer)
    await message.answer("Монтажник/закупщик. Наименование, ИНН")


@router.message(UserForm.inn_name_buyer)
async def form_inn_name_buyer(message: Message, state: FSMContext):
    await state.update_data(inn_name_buyer=message.text)
    await state.set_state(UserForm.inn_name_designer)
    await message.answer("Проектировщик. Наименование, ИНН")


@router.message(UserForm.inn_name_designer)
async def form_inn_name_designer(message: Message, state: FSMContext):
    await state.update_data(inn_name_designer=message.text)
    await state.set_state(UserForm.purchase_type)
    await message.answer("Тип закупки (прямая/тендер)")


@router.message(UserForm.purchase_type)
async def form_purchase_type(message: Message, state: FSMContext):
    await state.update_data(purchase_type=message.text)
    await state.set_state(UserForm.blank_num)
    await message.answer("Номер бланка регистрации объекта (по номеру КП)")


@router.message(UserForm.blank_num)
async def form_blank_num(message: Message, state: FSMContext):
    await state.update_data(blank_num=message.text)
    await state.set_state(UserForm.reg_date)
    await message.answer("Дата регистрации объекта")


@router.message(UserForm.reg_date)
async def form_reg_date(message: Message, state: FSMContext):
    await state.update_data(reg_date=message.text)
    await state.set_state(UserForm.manager)
    await message.answer("Персональный менеджер")


@router.message(UserForm.manager)
async def form_manager(message: Message, state: FSMContext):
    await state.update_data(manager=message.text)
    await state.set_state(UserForm.phone)
    await message.answer("Телефон")


@router.message(UserForm.phone)
async def form_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(UserForm.email)
    await message.answer("Почта")


@router.message(UserForm.email)
async def form_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    data = await state.get_data()
    await state.clear()
    data["document_link"] = ""
    record_id = await Db.add_object(tg_id=message.from_user.id, **data)
    reply_text = make_reply(data)
    keyboard = main_keyboard
    await state.set_state(EditForm.analyze),
    await state.update_data(record_id=record_id),
    await message.answer(reply_text, reply_markup=keyboard)


@router.message(F.document)
async def on_document(message: Message, bot: Bot, settings: Settings, state: FSMContext):
    doc = message.document
    assert doc is not None
    storage_root = Path(settings.storage_dir)
    user_dir = storage_root / str(message.from_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    saved_path: Optional[str] = None
    try:
        filename = doc.file_name or f"{doc.file_unique_id}.bin"
        destination = user_dir / f"{doc.file_unique_id}_{filename}"
        file = await bot.get_file(doc.file_id)
        await bot.download(file, destination=destination)
        saved_path = str(destination)
    except TelegramBadRequest as e:
        logging.exception("Failed to download document: %s", e)

    fields_dict = extract_table_from_blank(saved_path)
    name_flag, obj, service = await check_name_exist(fields_dict.get("name", ""))
    fields_dict["name_service"] = service
    inn_flag, obj, service = await check_inn_exist(fields_dict.get('inn_name_customer', ""))
    fields_dict["inn_name_customer_service"] = service
    adress_flag, obj, service = await check_adress_exist(fields_dict.get('adress', ""))
    fields_dict["adress_service"] = service
    if (name_flag or inn_flag or adress_flag):
        reply_text = make_reply(dict(obj))
        await state.set_state(UserForm.check_continue)
        await state.update_data(
            fields_dict=fields_dict,
            saved_path=saved_path
        )
        await message.answer("Данный объект уже добавлен в базу\n\n")
        await asyncio.sleep(2)
        await message.answer(reply_text, reply_markup=check_continue_keyboard)
        return

    record_id = await Db.add_object(
        tg_id=message.from_user.id,
        **fields_dict,
        document_link=saved_path
    )    
    keyboard = main_keyboard
    reply_text = make_reply(fields_dict)
    await state.set_state(EditForm.analyze),
    await state.update_data(record_id=record_id),
    await message.answer(reply_text, reply_markup=keyboard)


@router.callback_query(StateFilter(EditForm.analyze), F.data.startswith("edit"))
async def edit(callback: CallbackQuery, state: FSMContext):
    keyboard = edit_choose_keyboard
    await state.set_state(EditForm.edit)
    await state.update_data(main_message_id=int(callback.message.message_id))
    await callback.message.edit_reply_markup(
        inline_message_id=callback.inline_message_id,
        reply_markup=keyboard
    )


@router.callback_query(StateFilter(EditForm.analyze), F.data.startswith("confirm"))
async def edit(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(
        callback.message.chat.id,
        callback.message.message_id
    )
    await bot.send_message(
        callback.message.chat.id,
        "Объект успешно добавлен"
    )
    await state.clear()
    await asyncio.sleep(1)
    await bot.send_message(
        callback.message.chat.id,
        "Чтобы добавить объект загрузите бланк в формате 'pdf' или отправьте команду /form"
    )


@router.callback_query(StateFilter(EditForm.analyze), F.data.startswith("reject"))
async def edit(callback: CallbackQuery, bot: Bot, state: FSMContext):
    record_id = await state.get_value('record_id')
    flag = await Db.delete_object(record_id)
    if flag:
        await callback.message.delete()
        await bot.send_message(
            callback.message.chat.id,
            "Добавление объекта отменено успешно"
        )
        await state.clear()
        await bot.send_message(
            callback.message.chat.id,
            "Чтобы добавить объект загрузите бланк в формате 'pdf' или отправьте команду /form"
        )
    else:
        await bot.send_message(
            callback.message.chat.id,
            "Произшла ошибка при отмене добавления объекта"
        )


@router.callback_query(EditForm.edit)
async def answer(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditForm.edit_field)
    await state.update_data(field=callback.data)
    msg = await callback.message.answer(f"Введите новое значение для поля {callback.data}")
    await state.update_data(service_message_id=msg.message_id)


@router.message(EditForm.edit_field)
async def edit_field(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    res_flag = await Db.edit_object(data['record_id'], data['field'], message.text)
    if data['field'] in ["name", "inn_name_customer", "adress"]:
        if data['field'] == "name":
            _, _, service = await check_name_exist(message.text)
        if data['field'] == "inn_name_customer":
            _, _, service = await check_inn_exist(message.text)
        if data['field'] == "adress":
            _, _, service = await check_adress_exist(message.text)
        res_flag_service = await Db.edit_object(data['record_id'], data['field'] + '_service', service)
        if not res_flag_service:
            logging.warning(f"Adding service info for field {data['field']} has failed.")
    if res_flag:
        res_message = await message.answer("Данные успешно обновлены!")
    else:
        res_message = await message.answer("Произошла ошибка при редактировании")
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id
    )
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=data['service_message_id']
    )
    row = await Db.get_object("id", data['record_id'])
    reply_text = make_reply(dict(row))
    keyboard = main_keyboard
    await bot.edit_message_text(
        reply_text,
        chat_id=message.chat.id,
        message_id=data['main_message_id'],
        reply_markup=keyboard
    )
    await state.set_state(EditForm.analyze)
    await asyncio.sleep(3)
    await res_message.delete()


@router.callback_query(UserForm.check_continue)
async def check_continue(callback: CallbackQuery, bot: Bot, state: FSMContext):
    if callback.data == "continue":
        fields_dict = await state.get_value("fields_dict", None)
        if fields_dict:
            saved_path = await state.get_value("saved_path")
            record_id = await Db.add_object(
                tg_id=callback.message.from_user.id,
                **fields_dict,
                document_link=saved_path
            )    
            keyboard = main_keyboard
            reply_text = make_reply(fields_dict)
            await callback.message.delete()
            await state.clear()
            await state.set_state(EditForm.analyze),
            await state.update_data(record_id=record_id),
            await callback.message.answer(reply_text, reply_markup=keyboard)
        else:
            data = await state.get_data()
            next_state = data.pop("continue_state")
            next_text = data.pop("continue_text")
            await state.set_data(data)
            await state.set_state(next_state)
            await callback.message.delete()
            await asyncio.sleep(1)
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=next_text
            )
    elif callback.data == "reject":
        await callback.message.delete()
        await state.clear()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="Заполнение заявки отменено успешно"
        )
        await asyncio.sleep(1)
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="Чтобы добавить объект загрузите бланк в формате 'pdf' или отправьте команду /form"
        )
    else:
        await callback.message.delete()
        await state.clear()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="Чтобы добавить объект загрузите бланк в формате 'pdf' или отправьте команду /form"
        )


@router.message()
async def any_message(message: Message):
    await message.answer("Чтобы добавить объект загрузите бланк в формате 'pdf' или отправьте команду /form")
