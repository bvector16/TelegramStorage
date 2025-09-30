from __future__ import annotations
from typing import List, Iterable, Optional
import asyncpg


DDL_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id          bigserial PRIMARY KEY,
    tg_id       bigint UNIQUE NOT NULL,
    role        text NOT NULL DEFAULT 'user', -- roles: user, admin, banned
    created_at  timestamptz NOT NULL DEFAULT now()
);
"""
DDL_OBJECTS = """
CREATE TABLE IF NOT EXISTS objects (
    id bigserial PRIMARY KEY,
    tg_id bigint NOT NULL,
    name TEXT,
    name_service TEXT,
    inn_name_customer TEXT,
    inn_name_customer_service TEXT,
    inn_name_buyer TEXT,
    adress TEXT,
    adress_service TEXT,
    type TEXT,
    inn_name_gen_contr TEXT,
    inn_name_subcontr TEXT,
    inn_name_designer TEXT,
    purchase_type TEXT,
    blank_num TEXT,
    reg_date TEXT,
    manager TEXT,
    phone TEXT,
    email TEXT,
    document_link TEXT,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_inn_name_customer_service
ON objects(inn_name_customer_service);
CREATE INDEX IF NOT EXISTS idx_adress_service
ON objects(adress_service);
CREATE INDEX IF NOT EXISTS idx_name_service
ON objects(name_service);
"""


class Db:
    __pool: asyncpg.Pool

    @classmethod
    async def connect(cls, dsn: str) -> "Db":
        cls.__pool = await asyncpg.create_pool(dsn, min_size=1, max_size=10)
        async with cls.__pool.acquire() as conn:
            await conn.execute(DDL_USERS)
            await conn.execute(DDL_OBJECTS)

    @classmethod
    async def close(cls) -> None:
        await cls.__pool.close()

    @classmethod
    async def upsert_allowed_users(cls, tg_ids: Iterable[int], role: str = "user") -> None:
        if not tg_ids:
            return
        async with cls.__pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO users (tg_id, role)
                VALUES ($1, $2)
                ON CONFLICT (tg_id) DO UPDATE SET role = EXCLUDED.role
                """,
                [(int(tg_id), role) for tg_id in tg_ids],
            )

    @classmethod
    async def get_user_role(cls, tg_id: int) -> Optional[str]:
        async with cls.__pool.acquire() as conn:
            row = await conn.fetchrow("SELECT role FROM users WHERE tg_id = $1", tg_id)
            return row["role"] if row else None

    @classmethod
    async def set_user_role(cls, tg_id: int, role: str) -> None:
        async with cls.__pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (tg_id, role)
                VALUES ($1, $2)
                ON CONFLICT (tg_id) DO UPDATE SET role = EXCLUDED.role
                """,
                tg_id,
                role,
            )

    @classmethod
    async def add_object(
        cls,
        tg_id: Optional[int],
        name: Optional[str],
        name_service: Optional[str],
        inn_name_customer: Optional[str],
        inn_name_customer_service: Optional[str],
        adress: Optional[str],
        adress_service: Optional[str],
        type: Optional[str],
        inn_name_gen_contr: Optional[str],
        inn_name_subcontr: Optional[str],
        inn_name_buyer: Optional[str],
        inn_name_designer: Optional[str],
        purchase_type: Optional[str],
        blank_num: Optional[str],
        reg_date: Optional[str],
        manager: Optional[str],
        phone: Optional[str],
        email: Optional[str],
        document_link: Optional[str]
    ) -> int:
        async with cls.__pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO objects (tg_id, name, name_service, inn_name_customer, inn_name_customer_service, adress, adress_service, type, inn_name_gen_contr, inn_name_subcontr, inn_name_buyer, inn_name_designer, purchase_type, blank_num, reg_date, manager, phone, email, document_link)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19)
                RETURNING id
                """,
                tg_id,
                name,
                name_service,
                inn_name_customer,
                inn_name_customer_service,
                adress,
                adress_service,
                type,
                inn_name_gen_contr,
                inn_name_subcontr,
                inn_name_buyer,
                inn_name_designer,
                purchase_type,
                blank_num,
                reg_date,
                manager,
                phone,
                email,
                document_link
            )
            return int(row["id"])
        
    @classmethod
    async def edit_object(cls, id: int, field: str, value: str) -> bool:
        async with cls.__pool.acquire() as conn:
            result = await conn.execute(
                f"""
                UPDATE objects SET {field} = $1 WHERE id = $2
                """,
                value,
                id
            )
        return result.split()[-1] == '1'

    @classmethod
    async def get_object(cls, field_to_compare: str, value) -> asyncpg.Record:
        async with cls.__pool.acquire() as conn:
            row = await conn.fetch(
                f"""
                SELECT *
                FROM objects                
                WHERE {field_to_compare} = $1
                """,
                value
            )
            return row[0] if row else None
    
    @classmethod
    async def delete_object(cls, object_id: int) -> bool:
        async with cls.__pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM objects WHERE id = $1
                """,
                object_id
            )
            return result.split()[-1] == '1'
        
    @classmethod
    async def get_all(cls, field: str, role: str = 'user') -> List[str]:
        query = f"""SELECT {field} from objects"""
        async with cls.__pool.acquire() as conn:
            objects = await conn.fetch(query)
        return [obj[field] for obj in objects]
