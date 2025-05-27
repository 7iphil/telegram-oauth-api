from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import os
import hashlib
import hmac

# 🚀 FastAPI App
app = FastAPI()

# 🌐 CORS (открыто для всех доменов — можешь ограничить по хосту)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Настройки из переменных среды
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIRECT_URL = os.getenv("REDIRECT_URL", "https://your-site.com")

# ✅ Верификация подписи Telegram
def verify_telegram_auth(data: dict) -> bool:
    auth_data = data.copy()
    hash_received = auth_data.pop("hash", "")
    auth_data = sorted([f"{k}={v}" for k, v in auth_data.items()])
    data_check_string = "\n".join(auth_data)

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return calculated_hash == hash_received

# 🌐 POST /auth
@app.post("/auth")
async def auth(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not verify_telegram_auth(data):
        raise HTTPException(status_code=403, detail="Invalid Telegram Auth")

    # 🧠 Извлекаем данные
    user_id = data["id"]
    first_name = data.get("first_name", "")
    username = data.get("username", "")

    # 🌍 Формируем редирект (можно зашифровать или JWT)
    url = f"{REDIRECT_URL}?tg_id={user_id}&tg_name={first_name}&tg_username={username}"
    return RedirectResponse(url)

# 🔍 Для тестов
@app.get("/")
def index():
    return JSONResponse({"status": "ok", "bot_token": bool(BOT_TOKEN)})