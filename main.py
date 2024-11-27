from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers.start import start
from handlers.list_requests import list_requests
from handlers.cancel_request import cancel_request, handle_cancellation, handle_confirmation
from handlers.delete_account import delete_account, process_phone, process_code
from handlers.utils import load_requests
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

def update_bot(update, context):
    """
    Pulls the latest changes from GitHub and restarts the bot to apply updates.
    """
    update.message.reply_text("🔄 Updating bot to the latest version...")

    try:
        # Pull the latest changes from the repository
        git_pull = os.system("git pull")
        if git_pull != 0:
            raise Exception("Failed to pull the latest changes from GitHub.")
        
        update.message.reply_text("✅ Update successful! Restarting bot...")

        # Restart the bot without killing the VPS process
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        update.message.reply_text(f"❌ Update failed: {e}")


def main():
    # Load requests from JSON
    load_requests()

    # Get credentials from environment variables
    bot_token = os.getenv("BOT_TOKEN")

    # Initialize the bot
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("list_requests", list_requests))
    dispatcher.add_handler(CommandHandler("cancel_request", cancel_request))
    dispatcher.add_handler(CommandHandler("delete_account", delete_account))
    dispatcher.add_handler(CommandHandler("update_bot", update_bot))  # Add /update_bot command

    # Message handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_phone))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_code))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_cancellation))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_confirmation))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
