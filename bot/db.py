from __future__ import annotations
from typing import List, Literal, Iterable, Optional, overload
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
    inn_name_customer TEXT,
    inn_name_buyer TEXT,
    adress TEXT,
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
"""

# @dataclass(slots=True)
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

    # --- users ---
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

    # --- objects ---
    @classmethod
    async def add_object(
        cls,
        tg_id: Optional[int],
        name: Optional[str],
        inn_name_customer: Optional[str],
        adress: Optional[str],
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
                INSERT INTO objects (tg_id, name, inn_name_customer, adress, type, inn_name_gen_contr, inn_name_subcontr, inn_name_buyer, inn_name_designer, purchase_type, blank_num, reg_date, manager, phone, email, document_link)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
                RETURNING id
                """,
                tg_id,
                name,
                inn_name_customer,
                adress,
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
            return int(row["id"])  # pyright: ignore[reportOptionalSubscript]
        
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
    async def recent_objects(cls, tg_id: int, limit: int = 10) -> list[asyncpg.Record]:
        async with cls.__pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT *
                FROM objects
                WHERE tg_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                tg_id,
                limit,
            )
            return list(rows)

    @classmethod
    async def get_object(cls, object_id: int) -> asyncpg.Record:
        async with cls.__pool.acquire() as conn:
            row = await conn.fetch(
                """
                SELECT *
                FROM objects                
                WHERE id = $1
                """,
                object_id
            )
            return row[0]
    
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

    @overload
    @classmethod
    async def check_exists(cls, search_string: str, fields: List[str],
                           role: Literal['user', 'role']) -> tuple[bool, asyncpg.Record]: ...

    @overload
    @classmethod
    async def check_exists(cls, search_list: List[str], fields: List[str],
                           role: Literal['user', 'role']) -> tuple[bool, asyncpg.Record]: ...

    @classmethod
    async def check_exists(cls, search_string = None, search_list = None,
                           fields = ['name', 'inn_name_customer', 'adress'], role = 'user') -> tuple[bool, asyncpg.Record]:
        if not (search_string or search_list):
            raise ValueError("One of arguments must be set")
        conditions = []
        params = []

        if search_string:
            for i, field in enumerate(fields, 1):
                conditions.append(f"{field} ILIKE ${i}")
                params.append(f"%{search_string}%")
        else:
            for n, s in enumerate(search_list):
                for i, field in enumerate(fields, 1):
                    conditions.append(f"{field} ILIKE ${i + n * len(fields)}")
                    params.append(f"%{s}%")

        where_clause = " OR ".join(conditions)
        ids = ["id", "tg_id"] if role == 'admin' else []
        select_fields = [
            "name",
            "inn_name_customer",
            "adress",
            "type",
            "inn_name_gen_contr",
            "inn_name_subcontr",
            "inn_name_buyer",
            "inn_name_designer",
            "purchase_type",
            "blank_num",
            "reg_date",
            "manager",
            "phone",
            "email",
            "document_link"
        ]
        query = f"""
            SELECT {",".join(ids + select_fields)} FROM objects 
            WHERE {where_clause}
        """

        async with cls.__pool.acquire() as conn:
            objects = await conn.fetch(query, *params)
        if objects:
            return True, objects[0]
        else:
            return False, None
