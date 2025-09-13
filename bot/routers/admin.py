from aiogram.filters import Command
from aiogram.types import Message, BotCommandScopeDefault
from aiogram import Router, Bot
from routers.commands import user_commands, admin_commands
from utils.utils import make_reply
from db import Db
import html


admin_router = Router()


async def _ensure_admin(tg_id: int) -> bool:
    return (await Db.get_user_role(tg_id)) == "admin"


@admin_router.message(Command("promote"))
async def cmd_promote(message: Message, bot: Bot):
    if not await _ensure_admin(message.from_user.id):
        await message.answer("❌ Только для админа")
        return
    parts = message.text.split(maxsplit=2) if message.text else []
    if len(parts) < 2:
        await message.answer(f"Применение: /promote {html.escape("<telegram_id>")}")
        return
    try:
        target = int(parts[1])
    except ValueError:
        await message.answer("Неверный Telegram ID")
        return
    await Db.set_user_role(target, "admin")
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeDefault())
    await message.answer(f"✅ Статус админа присвоен пользователю с ID {target}")


@admin_router.message(Command("grant"))
async def cmd_grant(message: Message, bot: Bot):
    if not await _ensure_admin(message.from_user.id):
        await message.answer("❌ Только для админа")
        return
    parts = message.text.split(maxsplit=2) if message.text else []
    if len(parts) < 2:
        await message.answer(f"Применение: /grant {html.escape("<telegram_id>")}")
        return
    try:
        target = int(parts[1])
    except ValueError:
        await message.answer("Неверный Telegram ID")
        return
    await Db.set_user_role(target, "user")
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    await message.answer(f"✅ Доступ предоставлен пользователю с ID {target}")


@admin_router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if not await _ensure_admin(message.from_user.id):
        await message.answer("❌ Только для админа")
        return
    parts = message.text.split(maxsplit=2) if message.text else []
    if len(parts) < 2:
        await message.answer(f"Применение: /ban {html.escape("<telegram_id>")}")
        return
    try:
        target = int(parts[1])
    except ValueError:
        await message.answer("Неверный Telegram ID")
        return
    await Db.set_user_role(target, "banned")
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
    await message.answer(f"🚫 Доступ запрещен пользователю с ID {target}")


@admin_router.message(Command("delete"))
async def cmd_ban(message: Message):
    if not await _ensure_admin(message.from_user.id):
        await message.answer("❌ Только для админа")
        return
    parts = message.text.split(maxsplit=1) if message.text else []
    if len(parts) < 2:
        await message.answer(f"Применение: /delete {html.escape("<id объекта>")}")
        return
    target = int(parts[1])
    flag = await Db.delete_object(target)
    if flag:
        await message.answer("Объект успешно удален из базы")
    else:
        await message.answer("Не удалось удалить объект из базы")


@admin_router.message(Command("search"))
async def cmd_ban(message: Message):
    if not await _ensure_admin(message.from_user.id):
        await message.answer("❌ Только для админа")
        return
    parts = message.text.split(maxsplit=1) if message.text else []
    if len(parts) < 2:
        await message.answer(f"Применение: /search {html.escape("<search text>")}")
        return
    target = parts[1]
    flag, obj = await Db.check_exists(target, role='admin')
    if flag:
        reply_text = make_reply(dict(obj))
        await message.answer(reply_text)
    else:
        await message.answer("Объект не найден")
