import requests

# ==================== НАСТРОЙКИ СВЯЗИ ====================
DEEPSEEK_API_KEY = "sk-1fffe28edcbb4af3a025514002faeeea" 
TELEGRAM_BOT_TOKEN = "8661086712:AAH5q_Lu81OIaVVYLgptuKXh7vHK4ihRbVc"
TELEGRAM_CHAT_ID = "-1003220042819"

THRESHOLD_USD = 9999.0 
# =============================================================

def force_check_balance_now():
    ds_url = "https://deepseek.com"
    ds_headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(ds_url, headers=ds_headers)
        if response.status_code == 200:
            data = response.json()
            for info in data.get("balance_infos", []):
                if info.get("currency") == "USD":
                    current_balance = float(info.get("total_balance", 0))
                    if current_balance <= THRESHOLD_USD:
                        send_telegram_notification_group(current_balance)
                    return current_balance
        else:
            print(f"Сервер вернул статус {response.status_code}. Ответ: {response.text}")
    except Exception as e:
        print(f"Техническая ошибка: {e}")

def send_telegram_notification_group(balance):
    message = (
        f"🚨 **КРИТИЧЕСКИЙ БАЛАНС DEEPSEEK!** 🚨\n\n"
        f"Внимание всей команде отдела маркетинга!\n"
        f"Текущий остаток на API: **${balance:.2f}**\n\n"
        f"Срочно пополните счет, иначе работа встанет!"
    )
    
    # Прямая ссылка без склеек, чтобы у GitHub не было шанса запустить старый баг
    tele_url = "https://telegram.org"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(tele_url, json=payload)
    print(f"Статус отправки в Telegram: {res.status_code}")

if __name__ == "__main__":
    force_check_balance_now()
