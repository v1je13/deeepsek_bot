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
  // Защита от одновременных запусков.
  const lock = LockService.getScriptLock();

  if (!lock.tryLock(10000)) {
    Logger.log("Другой запуск уже отправляет уведомление.");
    return;
  }

  try {
    const properties = PropertiesService.getScriptProperties();

    // Отдельное сохранение для каждого бота и чата.
    const botId = TELEGRAM_BOT_TOKEN.split(":")[0];
    const propertyKey =
      "DEEPSEEK_LAST_MESSAGE_" + botId + "_" + TELEGRAM_CHAT_ID;

    const previousMessageId = properties.getProperty(propertyKey);

    const message =
      "🚨 <b>НИЗКИЙ БАЛАНС DEEPSEEK!</b> 🚨\n\n" +
      "Внимание всей команде отдела маркетинга!\n" +
      "Текущий остаток на API: <b>$" + balance.toFixed(2) + "</b>\n\n" +
      "Пополните счёт, чтобы избежать остановки работы.";

    // Сначала отправляем новое уведомление.
    const sent = telegramRequest("sendMessage", {
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: "HTML"
    });

    if (!sent || !sent.ok || !sent.result || !sent.result.message_id) {
      Logger.log("Новое уведомление не подтверждено. Старое сохранено.");
      return;
    }

    const newMessageId = String(sent.result.message_id);

    // Запоминаем ID между запусками скрипта.
    properties.setProperty(propertyKey, newMessageId);
    Logger.log("Новое уведомление отправлено. ID: " + newMessageId);

    // Удаляем только предыдущее уведомление этого скрипта.
    if (previousMessageId && previousMessageId !== newMessageId) {
      const deleted = telegramRequest("deleteMessage", {
        chat_id: TELEGRAM_CHAT_ID,
        message_id: Number(previousMessageId)
      });

      if (deleted && deleted.ok) {
        Logger.log("Предыдущее уведомление удалено.");
      } else {
        Logger.log(
          "Новое уведомление отправлено, но предыдущее удалить не удалось."
        );
      }
    }
  } catch (e) {
    // Не логируем исключение целиком: оно может содержать токен.
    Logger.log("Ошибка обновления уведомления. Тип: " + e.name);
  } finally {
    lock.releaseLock();
  }
}

function telegramRequest(method, payload) {
  const url =
    "https://api.telegram.org/bot" +
    TELEGRAM_BOT_TOKEN +
    "/" +
    method;

  try {
    const response = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    const status = response.getResponseCode();
    const data = JSON.parse(response.getContentText());

    Logger.log("Telegram " + method + ": HTTP " + status);

    if (status !== 200 || !data.ok) {
      Logger.log(
        "Ошибка Telegram: " + (data.description || "Неизвестная ошибка")
      );
      return null;
    }

    return data;
  } catch (e) {
    Logger.log("Ошибка запроса Telegram " + method + ". Тип: " + e.name);
    return null;
  }
}
  }

