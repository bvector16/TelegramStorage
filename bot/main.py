from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from middlewares import PermissionMiddleware
from routers.admin import admin_router
from routers.user import router
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import Settings
from pathlib import Path
from db import Db
import asyncio
import logging


async def main() -> None:
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = Settings.load()
    if not settings.bot_token or not settings.database_url:
        raise RuntimeError("BOT_TOKEN and DATABASE_URL must be set")

    # Ensure storage directory exists
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)

    # Db connect & bootstrap allowlist
    await Db.connect(settings.database_url)
    if settings.allowed_user_ids:
        await Db.upsert_allowed_users(settings.allowed_user_ids, role="admin" if len(settings.allowed_user_ids) == 1 else "user")

    # Bot
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Inject shared objects using aiogram's context storage
    dp.workflow_data.update({
        "settings": settings,
    })

    # Middlewares
    dp.message.middleware(PermissionMiddleware())

    # Routers
    dp.include_router(admin_router)
    dp.include_router(router)

    try:
        logging.info("Bot starting…")
        await dp.start_polling(bot, close_bot_session=True)
    finally:
        logging.info("Shutting down…")
        await Db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
