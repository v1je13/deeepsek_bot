import requests
import json

import os
import requests

# ==================== БЕЗОПАСНЫЕ НАСТРОЙКИ ====================
# Теперь скрипт ищет ключи в переменных окружения Render
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003220042819") # ID чата можно оставить, он не секретный
THRESHOLD_USD = float(os.getenv("THRESHOLD_USD", "10.0")) # Порог по умолчанию $10
# =============================================================

# Дальше весь остальной код скрипта остается без изменений...

def check_deepseek_balance():
    ds_url = "https://deepseek.com"
    ds_headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(ds_url, headers=ds_headers)
        
        # Если API ответило успешно
        if response.status_code == 200:
            data = response.json()
            
            # Пробегаемся по списку балансов и ищем валюту USD
            for info in data.get("balance_infos", []):
                if info.get("currency") == "USD":
                    current_balance = float(info.get("total_balance", 0))
                    
                    # Проверяем, не упал ли баланс ниже критического уровня
                    if current_balance <= THRESHOLD_USD:
                        send_telegram_alert(current_balance)
                    return current_balance
        else:
            print(f"Ошибка проверки баланса DeepSeek. Статус: {response.status_code}, Ответ: {response.text}")
            
    except Exception as e:
        print(f"Произошла ошибка при запросе к DeepSeek: {e}")

def send_telegram_alert(balance):
    # Формируем красивое сообщение с разметкой Markdown
    message = (
        f"🚨 **КРИТИЧЕСКИЙ БАЛАНС DEEPSEEK!** 🚨\n\n"
        f"Внимание всей команде! Баланс API упал ниже лимита.\n"
        f"Текущий остаток: **${balance:.2f}**\n\n"
        f"Срочно пополните счет, иначе через пару минут вся работа встанет!"
    )
    
    tele_url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(tele_url, json=payload)
        if res.status_code != 200:
            print(f"Ошибка отправки в Telegram: {res.text}")
    except Exception as e:
        print(f"Не удалось отправить уведомление в Telegram: {e}")

if __name__ == "__main__":
    check_deepseek_balance()
