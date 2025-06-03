from logging_setup import logger
from telegram import Update
from telegram.ext import ContextTypes
from supabase_setup import supabase
import os

DOMAIN = os.getenv("WEB_DOMAIN")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    try:
        # Delete the user's command message
        await update.message.delete()
    except Exception as e:
        logger.error(f"Failed to delete command message: {e}")

    # Send initial status message
    status_msg = await context.bot.send_message(
        chat_id=chat.id,
        text="⏳ Verifying the group type...",
        parse_mode="Markdown"
    )

    try:
        # 1. Ensure command is used in a supergroup
        if chat.type == "group":
            await status_msg.edit_text(
                "🟠 This is a *normal group*.\n\n"
                "⚠️ Teledict requires *supergroup* features to function correctly.\n"
                "Please convert this group to a supergroup:\n"
                "• Open group settings\n"
                "• Enable chat history for new members or set a public link\n\n"
                "Once converted, re-add me and use /confirm again.",
                parse_mode="Markdown"
            )
            logger.info(f"/confirm used in normal group by {user.username} ({user.id})")
            return
        elif chat.type != "supergroup":
            await status_msg.edit_text(f"❓ Unsupported chat type: {chat.type}")
            logger.info(f"/confirm used in unsupported chat type by {user.username} ({user.id})")
            return

        await status_msg.edit_text("✅ Group type verified. Checking bot admin status...", parse_mode="Markdown")

        # 2. Check if bot is admin
        bot_member = await chat.get_member(context.bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            await status_msg.edit_text("❌ I need to be an admin in this group to confirm it.", parse_mode="Markdown")
            logger.info(f"Bot is not admin in {chat.title} ({chat.id})")
            return

        await status_msg.edit_text("✅ Bot is admin. Checking if you are the group owner...", parse_mode="Markdown")

        # 3. Check if user is the owner (creator)
        user_member = await chat.get_member(user.id)
        if user_member.status != "creator":
            await status_msg.edit_text("❌ Only the group owner can confirm this group.", parse_mode="Markdown")
            logger.info(f"User {user.username} ({user.id}) is not the owner in {chat.title} ({chat.id})")
            return

        await status_msg.edit_text("✅ You are the group owner. Checking your Teledict profile...", parse_mode="Markdown")

        # 4. Check if user exists in 'users'
        profile_resp = supabase.table("users").select("telegram_id").eq("telegram_id", str(user.id)).execute()
        if not profile_resp.data:
            await status_msg.edit_text(f"❌ You must sign up at {DOMAIN} before confirming a group.", parse_mode="Markdown")
            logger.info(f"User {user.username} ({user.id}) not found in users table.")
            return

        await status_msg.edit_text("✅ Profile found. Checking if group already exists...", parse_mode="Markdown")

        # 5. Check if group already exists
        group_resp = supabase.table("listings").select("id").eq("telegram_chat_id", str(chat.id)).execute()
        if group_resp.data:
            await status_msg.edit_text("⚠️ This group is already listed in the directory.", parse_mode="Markdown")
            logger.info(f"Group {chat.title} ({chat.id}) already exists in groups table.")
            return

        await status_msg.edit_text("✅ Group not listed. Saving group to directory...", parse_mode="Markdown")

        # 6. Gather group data
        full_chat = await context.bot.get_chat(chat.id)
        title = full_chat.title
        type = full_chat.type
        username = getattr(full_chat, "username", None)
        invite_link = getattr(full_chat, "invite_link", None) or "No link set"
        member_count = await context.bot.get_chat_member_count(chat.id)

        # 7. Insert group into 'groups' table
        user_id = supabase.table("users").select("id").eq("telegram_id", str(user.id)).execute()
        group_data = {
            "telegram_chat_id": str(chat.id),
            "title": title,
            "username": username,
            "invite_link": invite_link,
            "member_count": member_count,
            "type": type,
            "submitted_by": user_id.data[0]["id"],
        }
        supabase.table("listings").insert(group_data).execute()
        logger.info(f"Group inserted: {title} ({chat.id}) by {user.username} ({user.id})")

     

        # 8. Success message
        await status_msg.edit_text(
            f"✅ Group confirmed!\n\n"
            f"Visit {DOMAIN}/group/{chat.id}/edit to finish setup.",
            parse_mode="Markdown"
        )
        logger.info(f"Confirmation message sent for group {chat.title} ({chat.id})")

    except Exception as e:
        logger.exception("Error during /confirm")
        try:
            await status_msg.edit_text("❌ An error occurred while confirming the group.", parse_mode="Markdown")
        except Exception:
            pass