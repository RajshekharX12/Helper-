def start(update, context):
    update.message.reply_text(
        "👋 Welcome to the Telegram Account Deletion Bot!\n\n"
        "Use the following commands:\n"
        "/delete_account - Delete or request account deletion\n"
        "/list_requests - View pending deletion requests\n"
        "/cancel_request - Cancel a pending deletion request\n"
        "Let's get started!"
    )
