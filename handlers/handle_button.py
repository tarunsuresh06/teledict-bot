from logging_setup import logger
from telegram import Update
from telegram.ext import ContextTypes

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.info(f"Button pressed: {query.data} by user {query.from_user.username} ({query.from_user.id})")

    if query.data == "add_group":
        await query.edit_message_text(
            "Step 1: Add this bot as an **admin** in your Telegram group.\n"
            "Step 2: Go to that group and send the command: `/confirm`",
            parse_mode="Markdown"
        )
        logger.info("Sent add_group instructions.")
        
    elif query.data == "view_groups":
        await query.edit_message_text("This feature is coming soon!")
        logger.info("Informed user that view_groups is coming soon.")