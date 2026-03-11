import os
import asyncio
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot e aktivен.\n"
        "Како owner, прати ми .txt фајл со chat IDs за broadcast."
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Само owner може да праќа фајл со IDs.")
        return

    doc: Document = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("Качи .txt фајл со по еден chat_id во ред.")
        return

    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()
    content = file_bytes.decode("utf-8")

    chat_ids = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            try:
                chat_ids.append(int(line))
            except ValueError:
                pass

    await update.message.reply_text(f"Найдени {len(chat_ids)} chat IDs. Пуштам broadcast...")

    text = "Поздрав, ова е тест порака од ботот за факултет 🙂"

    for cid in chat_ids:
        try:
            await context.bot.send_message(chat_id=cid, text=text)
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Грешка за {cid}: {e}")

    await update.message.reply_text("Готово, пораката е испратена до сите ID-и од фајлот (доколку се валидни).")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
