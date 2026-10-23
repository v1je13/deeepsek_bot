import requests

# ==================== ПРЯМЫЕ НАСТРОЙКИ СВЯЗИ ====================
# Вставляем данные напрямую, раз секреты GitHub пока не передаются
DEEPSEEK_API_KEY = "sk-d4eb2c9663fb4870909838f040f8d030" 
TELEGRAM_BOT_TOKEN = "8661086712:AAH5q_Lu81OIaVVYLgptuKXh7vHK4ihRbVc"
TELEGRAM_CHAT_ID = "-1003220042819"

# Жестко зашиваем панику для 100% прохождения теста
THRESHOLD_USD = 9999.0 
# =============================================================

def check_deepseek_balance():
    ds_url = "https://deepseek.com"
    ds_headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Accept": "application/json"
    }
    
    print("--- ЗАПУСК ДИАНГНОСТИКИ ---")
    try:
        response = requests.get(ds_url, headers=ds_headers)
        print(f"Статус ответа DeepSeek: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            for info in data.get("balance_infos", []):
                if info.get("currency") == "USD":
                    current_balance = float(info.get("total_balance", 0))
                    print(f"Успешно! Баланс в DeepSeek равен: ${current_balance}")
                    send_telegram_alert(current_balance)
                    return current_balance
        else:
            print(f"DeepSeek вернул ошибку: {response.text}")
    except Exception as e:
        print(f"Ошибка сети при запросе к DeepSeek: {e}")

def send_telegram_alert(balance):
    message = (
        f"🚨 **КРИТИЧЕСКИЙ БАЛАНС DEEPSEEK!** 🚨\n\n"
        f"Внимание всей команде отдела маркетинга!\n"
        f"Текущий остаток на API: **${balance:.2f}**\n\n"
        f"Срочно пополните счет, иначе работа встанет!"
    )
    
    tele_url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(tele_url, json=payload)
        print(f"Статус ответа Telegram: {res.status_code}")
        print(f"Текст ответа Telegram: {res.text}")
    except Exception as e:
        print(f"Ошибка сети при отправке в Telegram: {e}")

if __name__ == "__main__":
    check_deepseek_balance()
