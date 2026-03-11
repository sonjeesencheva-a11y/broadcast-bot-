import os
import asyncio
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot e aktiven.\n"
        "Kako owner, prati mi .txt fajl so chat IDs za broadcast."
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Samo owner moze da praka fajl so IDs.")
        return

    doc: Document = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("Kaci .txt fajl so po eden chat_id vo red.")
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

    await update.message.reply_text(f"Najdeni {len(chat_ids)} chat IDs. Pustam broadcast...")

    text = "Pozdrav, ova e test poraka od botot 🙂"

    for cid in chat_ids:
        try:
            await context.bot.send_message(chat_id=cid, text=text)
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Greska za {cid}: {e}")

    await update.message.reply_text("Gotovo, porakata e ispratena.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.run_polling()

if __name__ == "__main__":
    main()
