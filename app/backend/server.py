from fastapi import FastAPI
from tasks.send_message import send_message_to_user
app = FastAPI()


@app.post("/send-message/{user_id}")
async def daily(user_id):
    send_message_to_user.delay()
    return {"status": "queued", "user_id": user_id}