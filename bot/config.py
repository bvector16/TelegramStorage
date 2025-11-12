from __future__ import annotations
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional
import logging
import os


load_dotenv()


class Settings(BaseModel):
    bot_token: str = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    allowed_user_ids: list[int] = Field(default_factory=list, alias="ALLOWED_USER_IDS")
    storage_dir: str = Field(default="storage", alias="STORAGE_DIR")
    dadataru_token: str = Field(alias="DADATARU_TOKEN")
    dadataru_secret: str = Field(alias="DADATARU_SECRET")

    @classmethod
    def load(cls) -> "Settings":
        # Simple env loader; accepts comma-separated ALLOWED_USER_IDS
        def parse_allowed(value: Optional[str]) -> list[int]:
            if not value:
                return []
            out: list[int] = []
            for chunk in value.split(","):
                chunk = chunk.strip()
                if not chunk:
                    continue
                try:
                    out.append(int(chunk))
                except ValueError:
                    logging.warning("Skipping invalid user id in ALLOWED_USER_IDS: %s", chunk)
            return out

        env = {
            "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
            "DATABASE_URL": os.getenv("DATABASE_URL", ""),
            "ALLOWED_USER_IDS": parse_allowed(os.getenv("ALLOWED_USER_IDS")),
            "STORAGE_DIR": os.getenv("STORAGE_DIR", "storage"),
            "DADATARU_TOKEN": os.getenv("DADATARU_TOKEN", ""),
            "DADATARU_SECRET": os.getenv("DADATARU_SECRET", "")
        }
        return cls.model_validate(env)
