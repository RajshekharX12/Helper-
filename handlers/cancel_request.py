from handlers.utils import user_requests, save_requests
from scheduler.reminder_scheduler import scheduler

def cancel_request(update, context):
    user_id = str(update.effective_user.id)
    if user_id not in user_requests or not user_requests[user_id]:
        update.message.reply_text("📋 You have no pending account deletion requests to cancel.")
        return

    message = "❌ **Select the account deletion request to cancel:**\n\n"
    for i, request in enumerate(user_requests[user_id], 1):
        phone = request["phone"]
        end_time = request["end_time"]
        message += f"{i}. Phone: `{phone}` | Scheduled End: {end_time}\n"
    update.message.reply_text(message, parse_mode="Markdown")
    context.user_data["state"] = "awaiting_cancellation"

def handle_cancellation(update, context):
    user_id = str(update.effective_user.id)
    if context.user_data.get("state") != "awaiting_cancellation":
        return

    try:
        index = int(update.message.text.strip()) - 1
        if index < 0 or index >= len(user_requests[user_id]):
            raise ValueError("Invalid index")

        request = user_requests[user_id][index]
        context.user_data["pending_cancellation"] = {"index": index, "request": request}
        context.user_data["state"] = "awaiting_confirmation"

        update.message.reply_text(
            f"❓ Are you sure you want to cancel the deletion request for `{request['phone']}`?\n\n"
            "Reply with 'Yes' to confirm or 'No' to abort."
        )
    except (ValueError, IndexError):
        update.message.reply_text("❌ Invalid selection. Please enter a valid number from the list.")

def handle_confirmation(update, context):
    user_id = str(update.effective_user.id)
    if context.user_data.get("state") != "awaiting_confirmation":
        return

    response = update.message.text.strip().lower()
    if response == "yes":
        pending = context.user_data.get("pending_cancellation", {})
        if not pending:
            update.message.reply_text("❌ No request to cancel. Please try again.")
            return

        index = pending["index"]
        request = pending["request"]
        user_requests[user_id].pop(index)
        save_requests()

        for job in scheduler.get_jobs():
            if job.args[1] == request["phone"]:
                job.remove()

        update.message.reply_text(f"✅ Successfully canceled deletion request for `{request['phone']}`.")
    elif response == "no":
        update.message.reply_text("❌ Cancellation process aborted. Your request remains active.")
    else:
        update.message.reply_text("❌ Invalid response. Please reply with 'Yes' or 'No'.")

    context.user_data["state"] = None
