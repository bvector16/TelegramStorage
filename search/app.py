
from fastapi import FastAPI, Request
from model import searcher
import uvicorn
import uuid


app = FastAPI()

def make_client_id(ip: str, port: int, user_agent: str) -> str:
    name = f"{ip}:{port}:{user_agent}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, name))

@app.get('/health')
async def health_check():
    flag = searcher.health()
    if flag:
        return {"status": "error", "message": "Model not loaded"}, 500
    return {"status": "ok"}

@app.post("/simular_search")
async def answer_responding(user_data: Request):
    ip = user_data.client.host
    port = user_data.client.port
    ua = user_data.headers.get('user-agent', 'unknown')
    client_id = make_client_id(ip, port, ua)
    body = await user_data.json()
    query, compare_list  = body['query'], body['compare_list']
    coincidences = await searcher.search(query, compare_list)
    return {
        "coincidences": coincidences,
    }


if __name__ == '__main__':
    uvicorn.run("app:app", port=8000, reload=True)
