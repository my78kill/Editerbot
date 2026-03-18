import asyncio
from flask import Flask
from bot import main as bot_main

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# 🔥 IMPORTANT: background task start
@app.before_serving
async def startup():
    asyncio.create_task(bot_main())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
