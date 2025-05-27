from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import hashlib
import hmac
import os
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (разрешаем запросы от любых источников, можно ограничить)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIRECT_URL = os.getenv("REDIRECT_URL", "https://your-site.com")

def verify_telegram_auth(data: dict) -> bool:
    auth_data = data.copy()
    hash_received = auth_data.pop("hash", "")
    auth_data = sorted([f"{k}={v}" for k, v in auth_data.items()])
    data_check_string = "\n".join(auth_data)
    secret_key = hmac.new(
        key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return calculated_hash == hash_received

@app.post("/auth")
async def auth(request: Request):
    data = await request.json()
    if not verify_telegram_auth(data):
        raise HTTPException(status_code=403, detail="Invalid Telegram Auth")

    # Отправляем обратно параметры в WordPress (можно шифровать)
    user_id = data["id"]
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    username = data.get("username", "")

    # Можно делать JWT или прямую передачу
    url = f"{REDIRECT_URL}?tg_id={user_id}&tg_name={first_name}&tg_username={username}"
    return RedirectResponse(url)
