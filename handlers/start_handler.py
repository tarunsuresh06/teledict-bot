from logging_setup import logger
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"/start command from {user.id} ({user.username})")

    keyboard = [
        [InlineKeyboardButton("➕ Add Your Group", url="https://t.me/teledictofficial_bot?startgroup=true", callback_data="add_group")],
        [InlineKeyboardButton("📄 View My Groups", callback_data="view_groups")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to the Telegram Group Directory Bot!\n\nChoose an option below:",
        reply_markup=reply_markup
    )