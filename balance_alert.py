import requests

# ==================== ПРЯМЫЕ НАСТРОЙКИ СВЯЗИ ====================
DEEPSEEK_API_KEY = "sk-1fffe28edcbb4af3a025514002faeeea" 
TELEGRAM_BOT_TOKEN = "8661086712:AAH5q_Lu81OIaVVYLgptuKXh7vHK4ihRbVc"
TELEGRAM_CHAT_ID = "-1003220042819"

# Лимит $9999 для принудительного прохождения теста
THRESHOLD_USD = 9999.0 
# =============================================================

def check_deepseek_balance():
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
                    
                    if current_balance <= THRESHOLD_USD:
                        send_telegram_alert(current_balance)
                    return current_balance
        else:
            print(f"Ошибка DeepSeek API: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Ошибка на стороне DeepSeek: {e}")

def send_telegram_alert(balance):
    message = (
        f"🚨 **КРИТИЧЕСКИЙ БАЛАНС DEEPSEEK!** 🚨\n\n"
        f"Внимание всей команде отдела маркетинга!\n"
        f"Текущий остаток на API: **${balance:.2f}**\n\n"
        f"Срочно пополните счет, иначе работа встанет!"
    )
    
    # Ссылка строго выверена: api.telegram.org со всеми слэшами
    tele_url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(tele_url, json=payload)
    print(f"Ответ Telegram API: {res.status_code}, {res.text}")

if __name__ == "__main__":
    check_deepseek_balance()
