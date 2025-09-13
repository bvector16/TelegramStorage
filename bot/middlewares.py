from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Optional
from db import Db


class PermissionMiddleware(BaseMiddleware):
    """Blocks handling for users without a role in DB (or with role='banned').

    Allows public commands: /start, /help
    Admins are users with role='admin'.
    """

    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event: TelegramObject, data: dict):  # type: ignore[override]
        message: Optional[Message] = data.get("event_update", {}).message if isinstance(data.get("event_update", {}), dict) else data.get("event_update")
        # Aiogram v3 passes many event types; get Message if present via data['event_from_user']
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        text = None
        if isinstance(event, Message) and event.text:
            text = event.text

        # Allow public commands regardless of permission
        if text and (text.startswith("/start") or text.startswith("/help")):
            return await handler(event, data)

        role = await Db.get_user_role(user.id)
        if role in {"user", "admin"}:
            return await handler(event, data)

        # Not allowed
        if isinstance(event, Message):
            await event.answer("❌ Доступ запрещен, обратитесь к администратору")
        return  # stop propagation
