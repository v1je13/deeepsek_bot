// ==================== НАСТРОЙКИ ====================
const DEEPSEEK_API_KEY = "sk-1fffe28edcbb4af3a025514002faeeea";
const TELEGRAM_BOT_TOKEN = "8661086712:AAH5q_Lu81OIaVVYLgptuKXh7vHK4ihRbVc";
const TELEGRAM_CHAT_ID = "-1003220042819";


const THRESHOLD_USD = 15;
// ==================================================

function checkDeepSeekBalance() {
  const dsUrl = "https://api.deepseek.com/user/balance";

  const options = {
    method: "get",
    headers: {
      Authorization: "Bearer " + DEEPSEEK_API_KEY,
      Accept: "application/json"
    },
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(dsUrl, options);
    const responseCode = response.getResponseCode();

    Logger.log("Статус DeepSeek: " + responseCode);

    if (responseCode !== 200) {
      Logger.log("Ошибка API DeepSeek. HTTP " + responseCode);
      return;
    }

    const data = JSON.parse(response.getContentText());
    const balanceInfos = data.balance_infos || [];

    for (let i = 0; i < balanceInfos.length; i++) {
      if (balanceInfos[i].currency !== "USD") {
        continue;
      }

      const rawBalance = balanceInfos[i].total_balance;
      const currentBalance = Number(rawBalance);

      if (
        rawBalance === null ||
        rawBalance === undefined ||
        String(rawBalance).trim() === "" ||
        !Number.isFinite(currentBalance)
      ) {
        Logger.log("Ошибка: некорректное значение баланса.");
        return;
      }

      Logger.log("Баланс DeepSeek: $" + currentBalance.toFixed(2));

      if (currentBalance <= THRESHOLD_USD) {
        sendTelegramAlert(currentBalance);
      } else {
        Logger.log("Баланс выше порога. Уведомление не требуется.");
      }

      return;
    }

    Logger.log("Баланс в USD не найден.");
  } catch (e) {
    // Не выводим текст исключения: он может содержать URL с токеном.
    Logger.log("Ошибка проверки баланса. Тип: " + e.name);
  }
}

function sendTelegramAlert(balance) {
  const url =
    "https://api.telegram.org/bot" +
    TELEGRAM_BOT_TOKEN +
    "/sendMessage";

  const message =
    "🚨 <b>НИЗКИЙ БАЛАНС DEEPSEEK!</b> 🚨\n\n" +
    "Внимание всей команде отдела маркетинга!\n" +
    "Текущий остаток на API: <b>$" + balance.toFixed(2) + "</b>\n\n" +
    "Пополните счёт, чтобы избежать остановки работы.";

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: "HTML"
    }),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const result = JSON.parse(response.getContentText());

    Logger.log("Статус Telegram: " + responseCode);

    if (responseCode === 200 && result.ok === true) {
      Logger.log("Уведомление успешно отправлено в Telegram.");
    } else {
      Logger.log(
        "Ошибка Telegram: " +
        (result.description || "Неизвестная ошибка")
      );
    }
  } catch (e) {
    Logger.log("Ошибка отправки в Telegram. Тип: " + e.name);
  }
}
