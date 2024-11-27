from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from handlers.utils import add_reminder
import os

def delete_account(update, context):
    update.message.reply_text(
        "📱 Please provide your phone number in the format `+1234567890`.\nReply with the phone number to proceed.",
        parse_mode="Markdown",
    )
    context.user_data["state"] = "awaiting_phone"

def process_phone(update, context):
    if context.user_data.get("state") != "awaiting_phone":
        return

    phone = update.message.text.strip()
    context.user_data["phone"] = phone
    update.message.reply_text("✅ Phone number received. Please provide the login code sent to your Telegram account.")
    context.user_data["state"] = "awaiting_code"

def process_code(update, context):
    if context.user_data.get("state") != "awaiting_code":
        return

    phone = context.user_data.get("phone")
    code = update.message.text.strip()

    update.message.reply_text("🔐 Attempting to log in...")

    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    try:
        with TelegramClient(f"session_{update.effective_user.id}", api_id, api_hash) as client:
            client.sign_in(phone, code)

            if client.is_user_authorized():
                update.message.reply_text("✅ Successfully logged in. Deleting your account...")
                client(functions.account.DeleteAccountRequest(reason="Requested via bot"))
                update.message.reply_text("🗑️ Your account has been successfully deleted.")
            else:
                update.message.reply_text("❌ Unable to log in. Unknown error.")
    except SessionPasswordNeededError:
        update.message.reply_text("⚠️ Two-step verification is enabled. Requesting account deletion.")
        try:
            with TelegramClient(f"session_{update.effective_user.id}", api_id, api_hash) as client:
                client(functions.account.DeleteAccountRequest(reason="Requested via bot"))
                update.message.reply_text("🗓️ Done. Your account deletion has been requested. I'll remind you in 7 days.")
                add_reminder(update.effective_user.id, phone, context)
        except Exception as e:
            update.message.reply_text(f"❌ Failed to request account deletion: {e}")
    except Exception as e:
        update.message.reply_text(f"❌ Failed to log in: {e}")
    context.user_data["state"] = None
