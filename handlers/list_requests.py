from handlers.utils import user_requests, calculate_time_remaining

def list_requests(update, context):
    user_id = str(update.effective_user.id)
    if user_id not in user_requests or not user_requests[user_id]:
        update.message.reply_text("📋 You have no pending account deletion requests.")
        return

    message = "📋 **Your Pending Account Deletion Requests:**\n\n"
    for i, request in enumerate(user_requests[user_id], 1):
        phone = request["phone"]
        end_time = request["end_time"]
        time_remaining = calculate_time_remaining(end_time)
        message += f"{i}. Phone: `{phone}` | {time_remaining}\n"
    
    update.message.reply_text(message, parse_mode="Markdown")
