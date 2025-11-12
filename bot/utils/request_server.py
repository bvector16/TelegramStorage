from typing import List
import aiohttp


class Requset_server:
    @staticmethod
    async def objects_searcher_request(query: str, compare_list: List[str]) -> List[str]:
        url = "http://localhost:8000/simular_search"
        payload = {
            "query": query,
            "compare_list": compare_list
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                json_response = await response.json() if response.status == 200 else None
        result = json_response.get('coincidences') if json_response else None
        return result
