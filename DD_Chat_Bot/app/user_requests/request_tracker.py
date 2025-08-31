import json
import os
from datetime import datetime, timedelta

REQUESTS_FILE = os.path.join(os.path.dirname(__file__), "user_requests.json")
REQUEST_LIMIT = 5

def load_requests():
    if not os.path.exists(REQUESTS_FILE):
        return {}
    with open(REQUESTS_FILE, "r") as f:
        return json.load(f)

def save_requests(data):
    with open(REQUESTS_FILE, "w") as f:
        json.dump(data, f)

def clean_old_requests(data):
    cutoff = datetime.now() - timedelta(hours=24)
    for user_id in list(data.keys()):
        ts = datetime.fromisoformat(data[user_id]["timestamp"])
        if ts < cutoff:
            del data[user_id]
    return data

def check_and_update_user_limit(user_id):
    data = load_requests()
    data = clean_old_requests(data)
    user = data.get(user_id)
    now = datetime.now().isoformat()
    if user:
        if user["count"] >= REQUEST_LIMIT:
            return False
        user["count"] += 1
        user["timestamp"] = now
    else:
        data[user_id] = {"userid": user_id, "count": 1, "timestamp": now}
    save_requests(data)
    return True