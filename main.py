from fastapi import FastAPI, Request
import requests

app = FastAPI()

TELEGRAM_TOKEN = "your_telegram_token"
GIGACHAT_TOKEN = "your_gigachat_token"

# Храним историю сообщений по chat_id
chat_history = {}

# Webhook для Telegram
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    chat_id = data["message"]["chat"]["id"]
    user_message = data["message"]["text"]

    # Добавляем сообщение в историю
    history = chat_history.get(chat_id, [])
    history.append({"role": "user", "content": user_message})

    # Отправляем историю в GigaChat
    response = requests.post(
        "https://gigachat-api-url.com/chat/completions",
        headers={"Authorization": f"Bearer {GIGACHAT_TOKEN}"},
        json={
            "model": "GigaChat",
            "messages": history
        }
    )
    assistant_reply = response.json()["choices"][0]["message"]["content"]

    # Добавляем ответ в историю
    history.append({"role": "assistant", "content": assistant_reply})
    chat_history[chat_id] = history[-10:]  # ограничиваем до 10 сообщений

    # Отправляем ответ в Telegram
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": assistant_reply}
    )

    return {"ok": True}
