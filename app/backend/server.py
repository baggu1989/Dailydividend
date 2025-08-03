from fastapi import FastAPI
from tasks.send_message import send_message_to_user

app = FastAPI()


@app.post("/daily-dividend/v1/send-message/{user_id}")
async def daily(user_id):
    send_message_to_user.delay()
    return {"status": "queued", "user_id": user_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)

