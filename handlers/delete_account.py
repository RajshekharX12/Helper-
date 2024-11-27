from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError
from handlers.utils import add_reminder
import os
import asyncio

async def send_code(phone, user_id):
    """
    Asynchronously sends a login code using Telethon.
    """
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    async with TelegramClient(f"session_{user_id}", api_id, api_hash) as client:
        await client.send_code_request(phone)


async def sign_in_and_delete(phone, code, user_id):
    """
    Asynchronously logs in and deletes the account using Telethon.
    """
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    async with TelegramClient(f"session_{user_id}", api_id, api_hash) as client:
        await client.sign_in(phone, code)
        await client(functions.account.DeleteAccountRequest(reason="Requested via bot"))


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
    user_id = update.effective_user.id

    update.message.reply_text("🔐 Sending login code to your Telegram account...")

    # Run the async function in the current thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(send_code(phone, user_id))
        update.message.reply_text(
            "✅ Login code sent to your Telegram account. Please provide the code here to proceed."
        )
        context.user_data["state"] = "awaiting_code"
    except PhoneNumberInvalidError:
        update.message.reply_text("❌ Invalid phone number. Please try again with a valid number.")
        context.user_data["state"] = None
    except Exception as e:
        update.message.reply_text(f"❌ Failed to send login code: {e}")
        context.user_data["state"] = None
    finally:
        loop.close()


def process_code(update, context):
    if context.user_data.get("state") != "awaiting_code":
        return

    phone = context.user_data.get("phone")
    code = update.message.text.strip()
    user_id = update.effective_user.id

    update.message.reply_text("🔐 Attempting to log in...")

    # Run the async function in the current thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(sign_in_and_delete(phone, code, user_id))
        update.message.reply_text("🗑️ Your account has been successfully deleted.")
    except SessionPasswordNeededError:
        # Handle two-step verification
        update.message.reply_text(
            "⚠️ Two-step verification is enabled. I will request account deletion for you now."
        )
        try:
            loop.run_until_complete(
                sign_in_and_delete(phone, None, user_id)
            )  # Request deletion without logging in
            update.message.reply_text(
                "🗓️ Done. Your account deletion has been requested. I'll remind you in 7 days."
            )
            add_reminder(update.effective_user.id, phone, context)
        except Exception as e:
            update.message.reply_text(f"❌ Failed to request account deletion: {e}")
    except Exception as e:
        update.message.reply_text(f"❌ Failed to log in: {e}")
    finally:
        loop.close()

    # Reset state
    context.user_data["state"] = None
