from logging_setup import logger
from telegram import Update
from telegram.ext import ContextTypes
from supabase_setup import supabase  

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