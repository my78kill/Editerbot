import asyncio
import threading
from flask import Flask
from bot import main as bot_main

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_main())

# ✅ Proper async thread
loop = asyncio.new_event_loop()
t = threading.Thread(target=start_async_loop, args=(loop,))
t.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
