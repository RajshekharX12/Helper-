from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers.start import start
from handlers.list_requests import list_requests
from handlers.cancel_request import cancel_request, handle_cancellation, handle_confirmation
from handlers.delete_account import delete_account, process_phone, process_code
from handlers.utils import load_requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Load requests from JSON
    load_requests()

    # Get credentials from environment variables
    import os
    bot_token = os.getenv("BOT_TOKEN")

    # Initialize the bot
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("list_requests", list_requests))
    dispatcher.add_handler(CommandHandler("cancel_request", cancel_request))
    dispatcher.add_handler(CommandHandler("delete_account", delete_account))

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
