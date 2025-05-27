# 🚀 Telegram OAuth API for WordPress

FastAPI сервис для авторизации пользователей через Telegram Bot Button.

## 📦 Features

- ✅ Подпись `hash` проверяется по Bot Token
- ✅ Возвращает redirect обратно в WP с tg_id и username

## 🌍 Endpoint

`POST /auth`

### 📥 Пример JSON тела:
```json
{
  "id": 123456789,
  "first_name": "Phil",
  "username": "ninja",
  "hash": "telegram_signed_hash_here"
}