import os
import requests

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003220042819")

# Жестко зашиваем панику для 100% теста
THRESHOLD_USD = 9999.0 

def check_deepseek_balance():
    ds_url = "https://deepseek.com"
    ds_headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Accept": "application/json"
    }
    
    print("--- ДИАГНОСТИКА DEEPSEEK ---")
    print(f"Используемый API-ключ (первые 7 символов): {str(DEEPSEEK_API_KEY)[:7]}...")
    
    try:
        response = requests.get(ds_url, headers=ds_headers)
        print(f"Ответ от DeepSeek API: Статус {response.status_code}")
        print(f"Текст ответа DeepSeek: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            for info in data.get("balance_infos", []):
                if info.get("currency") == "USD":
                    current_balance = float(info.get("total_balance", 0))
                    print(f"Баланс успешно определен: ${current_balance}")
                    send_telegram_alert(current_balance)
                    return current_balance
        else:
            # Если DeepSeek вернул ошибку, все равно пытаемся пнуть Telegram, чтобы проверить связь
            send_telegram_alert(f"Ошибка DeepSeek API: {response.status_code}")
            
    except Exception as e:
        print(f"Критическая ошибка запроса к DeepSeek: {e}")
        send_telegram_alert(f"Ошибка сети скрипта: {e}")

def send_telegram_alert(balance_or_error):
    if isinstance(balance_or_error, float):
        message = f"🚨 **ТЕСТ БАЛАНСА DEEPSEEK** 🚨\n\nТекущий остаток: **${balance_or_error:.2f}**"
    else:
        message = f"🚨 **ТЕСТОВАЯ ОШИБКА** 🚨\n\nДетали: {balance_or_error}"
    
    tele_url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    print("\n--- ДИАГНОСТИКА TELEGRAM ---")
    print(f"Используемый Токен (первые 10 символов): {str(TELEGRAM_BOT_TOKEN)[:10]}...")
    print(f"Используемый Chat ID: {TELEGRAM_CHAT_ID}")
    
    try:
        res = requests.post(tele_url, json=payload)
        print(f"Ответ от Telegram API: Статус {res.status_code}")
        print(f"Текст ответа Telegram: {res.text}")
    except Exception as e:
        print(f"Не удалось отправить запрос в Telegram: {e}")

if __name__ == "__main__":
    check_deepseek_balance()
