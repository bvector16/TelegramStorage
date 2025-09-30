from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from asyncpg import Record
from db import Db
import logging
import aiohttp
import re
import os


load_dotenv()


def make_reply(fields_dict: Dict) -> List[str]:
    ids = []
    id = fields_dict.get('id')
    tg_id = fields_dict.get('tg_id')
    if id and tg_id:
        ids = [
            f"<b>id:</b>\n{id}",
            f"<b>tg_id:</b>\n{tg_id}"    
        ]
    reply = [
        f"<b>Наименование объекта:</b>\n{fields_dict.get('name')}",        
        f"<b>Наименование, ИНН конечного заказчика:</b>\n{fields_dict.get('inn_name_customer')}",
        f"<b>Адрес объекта:</b>\n{fields_dict.get('adress')}",
        f"<b>Тип:</b>\n{fields_dict.get('type')}",
        f"<b>Ген. Подрядчик. Наименование, ИНН:</b>\n{fields_dict.get('inn_name_gen_contr')}",
        f"<b>Субподрядчик. Наименование, ИНН:</b>\n{fields_dict.get('inn_name_subcontr')}",
        f"<b>Монтажник/закупщик. Наименование, ИНН:</b>\n{fields_dict.get('inn_name_buyer')}",
        f"<b>Проектировщик. Наименование, ИНН:</b>\n{fields_dict.get('inn_name_designer')}",
        f"<b>Тип закупки (прямая/тендер):</b>\n{fields_dict.get('purchase_type')}",
        f"<b>Номер бланка регистрации объекта (по\nномеру КП):</b>\n{fields_dict.get('blank_num')}",
        f"<b>Дата регистрации объекта:</b>\n{fields_dict.get('reg_date')}",
        f"<b>Персональный менеджер:</b>\n{fields_dict.get('manager')}",
        f"<b>Телефон:</b>\n{fields_dict.get('phone')}",
        f"<b>Почта:</b>\n{fields_dict.get('email')}",
    ]
    if fields_dict.get('document_link'):
        reply.append(f"<b>Ссылка на бланк:</b>\n{fields_dict.get('document_link')}")
    reply = f"\n\n".join(ids + reply)
    return reply


async def dadataru_request(query: str) -> Optional[str]:
    url = "https://cleaner.dadata.ru/api/v1/clean/address"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {os.getenv("DADATARU_TOKEN")}",
        "X-Secret": os.getenv("DADATARU_SECRET")
    }
    json = [query]

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json) as response:
            response_json = await response.json() if response.status == 200 else None
    if not response_json:
        logging.warning(f"Dadata.ru request returned with error: {response.status}")
        return None
    city_street = (response_json[0]["city"] if response_json[0]["city"] else response_json[0]["region"]) + ', ' + response_json[0]["street"]
    return city_street


async def check_adress_exist(query: str) -> Tuple[bool, Optional[Record]]:
    if query in ["-", "—"]:
        return False, None, query
    try:
        query = await dadataru_request(query)
    except Exception as e:
        logging.warning(f"Dadata.ru request returned with error: {e}")
        query = None
    if not query:
        return False, None, ""
    exist_obj = await Db.get_object("adress_service", query)
    if exist_obj:
        return True, exist_obj, query
    return False, None, query


def extract_inn(text):
    pattern = r'(?:ИНН\s*)?(\d{10,12})'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None


async def check_inn_exist(query: str) -> Tuple[bool, Optional[Record]]:
    if query in ["-", "—"]:
        return False, None, query
    input_inn = extract_inn(query)
    if not input_inn:
        return False, None, ""
    exist_obj = await Db.get_object("inn_name_customer_service", input_inn)
    if exist_obj:
        return True, exist_obj, input_inn
    return False, None, input_inn


async def check_name_exist(query: str) -> Tuple[bool, Optional[Record]]:
    if query in ["-", "—"]:
        return False, None, query
    translate_table = str.maketrans('', '', ' ,.:"«»/()[]{}<>?!№;-–\'')
    query = query.translate(translate_table)
    if not query:
        return False, None, ""
    exist_obj = await Db.get_object("name_service", query)
    if exist_obj:
        return True, exist_obj, query
    return False, None, query
