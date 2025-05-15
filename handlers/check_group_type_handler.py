from telegram import Update
from telegram.ext import ContextTypes
from logging_setup import logger  # optional logging module

async def checkgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_type = chat.type
    chat_id = chat.id
    title = chat.title or "N/A"

    logger.info(f"/checkgroup used in {title} ({chat_id}) - type: {chat_type}")

    try:
        # Delete the user's command message
        await update.message.delete()
    except Exception as e:
        logger.error(f"Failed to delete command message: {e}")

    if chat_type == "private":
        await update.message.reply_text("👤 This is a private chat.")
    elif chat_type == "group":
        await update.message.reply_text(
            "🟠 This is a *normal group*.\n\n"
            "⚠️ Teledict requires *supergroup* features to function correctly.\n"
            "Please convert this group to a supergroup:\n"
            "• Open group settings\n"
            "• Enable chat history for new members or set a public link\n\n"
            "Once converted, re-add me and use /confirm again.",
            parse_mode="Markdown"
        )
    elif chat_type == "supergroup":
        await update.message.reply_text(
            "✅ This is a *supergroup*. You're good to go!",
            parse_mode="Markdown"
        )
    elif chat_type == "channel":
        await update.message.reply_text("📣 This is a channel, not a group.")
    else:
        await update.message.reply_text(f"❓ Unknown chat type: {chat_type}")
