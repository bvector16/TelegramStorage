from aiogram.types import BotCommand


user_commands = [
    BotCommand(command='start', description='Запустить бота'),
    BotCommand(command='form', description='Ввести данные объекта вручную'),
    BotCommand(command='help', description='Описание работы бота'),
]

admin_commands = [
    BotCommand(command='search', description='Найти объект'),
    BotCommand(command='delete', description='Удалить объект по id'),
    BotCommand(command='promote', description='Присвоить пользователю статус админа по id'),
    BotCommand(command='grant', description='Предоставить пользователю доступ по его id'),
    BotCommand(command='ban', description='Запретить пользователю доступ по его id'),
]
admin_commands = user_commands + admin_commands
