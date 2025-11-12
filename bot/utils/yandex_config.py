import json


with open("bot/utils/yandex_config.json") as f:
    config = json.load(f)


class Config:
    yandex_oauth: str = config.get("yandex_oauth")
    yandex_folder_id: str = config.get("yandex_folder_id")
    yandex_iam_token_url: str = config.get("yandex_iam_token_url")
    yandex_completion_url: str = config.get("yandex_completion_url")


config = Config()
