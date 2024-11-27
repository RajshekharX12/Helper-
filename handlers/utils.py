import json
from datetime import datetime, timedelta

DATA_FILE = "data/data.json"
user_requests = {}

def load_requests():
    global user_requests
    try:
        with open(DATA_FILE, "r") as file:
            user_requests = json.load(file)
    except FileNotFoundError:
        user_requests = {}

def save_requests():
    with open(DATA_FILE, "w") as file:
        json.dump(user_requests, file, indent=4)

def add_reminder(user_id, phone, context):
    end_time = datetime.now() + timedelta(days=7)
    if str(user_id) not in user_requests:
        user_requests[str(user_id)] = []
    user_requests[str(user_id)].append({"phone": phone, "end_time": end_time.isoformat()})
    save_requests()

def calculate_time_remaining(end_time):
    now = datetime.now()
    end_time = datetime.fromisoformat(end_time)
    delta = end_time - now
    if delta.total_seconds() <= 0:
        return "🔔 Deletion period has ended."
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds remaining."
