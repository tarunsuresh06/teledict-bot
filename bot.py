import logging
from logging.handlers import RotatingFileHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# ====== Logging Setup ======
logger = logging.getLogger("telegram-bot")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=3)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

load_dotenv()
# ====== Supabase Setup ======
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not SUPABASE_URL or not SUPABASE_KEY or not BOT_TOKEN:
    logger.error("Missing required environment variables. Please check your .env file.")
    raise EnvironmentError("Missing required environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logger.info("Supabase client initialized successfully.")

# ====== Bot Token ======
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ====== Supabase Save Function ======
def save_group(chat, invite_link, member_count, user_id):
    try:
        data = {
            "telegram_id": str(chat.id),
            "title": chat.title,
            "description":  "",
            "invite_link":  invite_link or"",
            "member_count": member_count,
            "submitted_by": str(user_id)
        }
        supabase.table("groups").insert(data).execute()
        logger.info(f"Saved group: {chat.title} ({chat.id})")
    except Exception as e:
        logger.exception("Failed to save group to Supabase")

# ====== Handlers ======
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

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_group":
        await query.edit_message_text(
            "Step 1: Add this bot as an **admin** in your Telegram group.\n"
            "Step 2: Go to that group and send the command: `/confirm`",
            parse_mode="Markdown"
        )
        
    elif query.data == "view_groups":
        await query.edit_message_text("This feature is coming soon!")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    full_chat = await context.bot.get_chat(chat.id)

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Please use this command inside a group where the bot is added.")
        return

    logger.info(f"/confirm used in {chat.title} ({chat.id}) by {user.username} ({user.id})")

    try:
        # Check if bot is admin
        bot_member = await chat.get_member(context.bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ I need to be an admin in this group to confirm it.")
            return

        # Check if already in DB
        existing = supabase.table("groups").select("id").eq("telegram_id", str(chat.id)).execute()
        if existing.data:
            await update.message.reply_text("⚠️ This group is already listed in the directory.")
            return

        # Optional: you can also check if the user is admin of the group
        user_member = await chat.get_member(user.id)
        if user_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Only a group admin can confirm this group.")
            return

        # Gather data
        title = full_chat.title
        description = full_chat.description or "No description"
        invite_link = full_chat.invite_link or "No link set"
        member_count = await context.bot.get_chat_member_count(chat.id)

        # Save to Supabase
        save_group(chat, invite_link, member_count, user.id)

        await update.message.reply_text(
            f"✅ *Group confirmed and added!*\n\n"
            f"**Title:** {title}\n"
            f"**Members:** {member_count}\n"
            f"**Invite Link:** {invite_link}",
            parse_mode="Markdown"
        )
        logger.info(f"Group confirmed and saved: {title} ({chat.id})")
        
    except Exception as e:
        logger.exception("Error during /confirm")
        await update.message.reply_text("❌ An error occurred while confirming the group.")

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