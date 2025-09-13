from typing import Dict, List


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
