from logging_setup import logger
from handlers.start_handler import start
from handlers.handle_button import handle_button
from handlers.confirm_handler import confirm
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os

# ====== Load Environment Variables ======
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("Missing BOT_TOKEN environment variable. Please check your .env file.")
    raise EnvironmentError("Missing BOT_TOKEN environment variable.")

# ====== Main ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(CommandHandler("confirm", confirm))

    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()