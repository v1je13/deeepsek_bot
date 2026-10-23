import os
import requests

# ==================== БЕЗОПАСНЫЕ НАСТРОЙКИ ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003220042819")

# Жестко зашиваем огромный порог для теста, чтобы бот СТОПРОЦЕНТНО отправил сообщение
THRESHOLD_USD = 9999.0 
# =============================================================

def check_deepseek_balance():
    # ТУТ БЫЛА ОШИБКА! Теперь адрес правильный:
    ds_url = "https://deepseek.com"
    ds_headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(ds_url, headers=ds_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            for info in data.get("balance_infos", []):
                if info.get("currency") == "USD":
                    current_balance = float(info.get("total_balance", 0))
                    
                    # Проверяем лимит
                    if current_balance <= THRESHOLD_USD:
                        send_telegram_alert(current_balance)
                    return current_balance
        else:
            print(f"Ошибка DeepSeek. Статус: {response.status_code}, Ответ: {response.text}")
            # Если DeepSeek ругнется на ключ — мы принудительно отправим ошибку в чат
            send_telegram_alert(f"Ошибка API Ключа ({response.status_code})")
            
    except Exception as e:
        print(f"Произошла ошибка при запросе к DeepSeek: {e}")
        send_telegram_alert(f"Ошибка сети скрипта: {e}")

def send_telegram_alert(balance_or_error):
    # Универсальный текст для теста
    if isinstance(balance_or_error, float):
        message = (
            f"🚨 **КРИТИЧЕСКИЙ БАЛАНС DEEPSEEK!** 🚨\n\n"
            f"Текущий остаток: **${balance_or_error:.2f}**\n"
            f"Срочно пополните счет!"
        )
    else:
        message = f"🚨 **ОШИБКА СКРИПТА КОНТРОЛЯ БАЛАНСА!** 🚨\n\nТехнические детали: {balance_or_error}"
    
    # ТУТ БЫЛА ОШИБКА! Теперь адрес API Telegram правильный:
    tele_url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(tele_url, json=payload)
        if res.status_code != 200:
            print(f"Ошибка Telegram API. Статус: {res.status_code}, Ответ: {res.text}")
    except Exception as e:
        print(f"Не удалось отправить уведомление в Telegram: {e}")

if __name__ == "__main__":
    check_deepseek_balance()
