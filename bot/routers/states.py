from aiogram.fsm.state import State, StatesGroup


class UserForm(StatesGroup):
    object_name = State()
    inn_name_customer = State()
    adress = State()
    type = State()
    inn_name_gen_contr = State()
    inn_name_subcontr = State()
    inn_name_buyer = State()
    inn_name_designer = State()
    purchase_type = State()
    blank_num = State()
    reg_date = State()
    manager = State()
    phone = State()
    email = State()
    edit = State()
    check_continue = State()
    check_doc_continue = State()


class EditForm(StatesGroup):
    analyze = State()
    edit = State()
    edit_field = State()
