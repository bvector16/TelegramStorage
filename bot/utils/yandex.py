from utils.yandex_config import config
from typing import List
import aiohttp
import urllib
import json


class Yandex:
    """Class for content generation with Yandex services"""
    def __init__(self):
        self.__oauth = config.yandex_oauth
        self.__iam_token_url = config.yandex_iam_token_url
        self.__iam_token = self.__get_iam_token()
        self.__folder_id = config.yandex_folder_id
        self.__completion_url = config.yandex_completion_url       
        self._data = {}
        self._data["modelUri"] = f"gpt://{self.__folder_id}/yandexgpt"
        self._data["completionOptions"] = {"temperature": 0.3, "maxTokens": 1000}

    def __get_iam_token(self):
        """Get IAM token"""
        data = json.dumps({"yandexPassportOauthToken": self.__oauth}).encode('utf-8')
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(self.__iam_token_url, data=data) as response:
        #         iam_raw = await response.read().decode('utf-8')
        iam_token_url = urllib.request.Request(url=self.__iam_token_url, data=data, method='POST')
        with urllib.request.urlopen(iam_token_url) as response:
            iam_raw = response.read().decode('utf-8')
        iam_token = json.loads(iam_raw).get('iamToken')
        return iam_token
        
    async def _llm_call(self, query: str, system_prompt: str):
        """YandexGPT completion"""
        self._data["messages"] = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": query},
        ]
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__iam_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.__completion_url, headers=headers, json=self._data) as response:
                response_json = await response.json()
        # response = requests.post(
        #     self.__completion_url,
        #     headers={
        #         "Accept": "application/json",
        #         "Authorization": f"Bearer {self.__iam_token}"
        #     },
        #     json=self._data,
        # ).json()
        return response_json["result"]["alternatives"][0]["message"]["text"]

    async def check_coincidence(self, query: str,  compare_list: List[str]) -> bool:
        system_prompt = "Твоя задача, есть ли искомый адрес в списке уже существующих\n---\nПравила:\n- Верни ТОЛЬКО номер совпадающей строки, если она есть, иначе -1"
        user_input = f"Искомый адрес:\n{query}\nCуществующие адреса:\n{"\n".join([f"{i}. {text}" for i, text in enumerate(compare_list)])}"
        coince_index = await self._llm_call(user_input, system_prompt)
        try:
            coince_index = int(coince_index)
            if coince_index < -1 or coince_index > 2:
                coince_index = -1
        except:
            coince_index = -1
        return coince_index


yandex_client = Yandex()
