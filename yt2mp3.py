#!/data/data/com.termux/files/usr/bin/python3
import threading
import os
from YT2mp3bot.downloader import main

print("YT2mp3 bot is starting...")

# Dummy Flask server to keep Render Web Service alive
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "YT2mp3 bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Flask server in a separate thread
    threading.Thread(target=run_flask).start()
    # Start your Telegram bot
    main()
