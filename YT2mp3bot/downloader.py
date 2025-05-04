#!/usr/bin/env python3
import sys
import os
import time
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue
import concurrent.futures
import yaml
from . import download_queue


try:
  from tg_token import TG_TOKEN
except ImportError:
  print('''
Rename the file tg_token_example.py to tg_token.py and make sure you gather
a Telegram bot token from @BotFather and place it in the file.
The token should be a string and look like this:
TG_TOKEN = '0123456789:Aa1Bb_Cc2Dd3Ee4Ff5Gg_-6Hh7Ii8JjKk9L'
''')
  sys.exit(1)

'''
Feel free to choose a different path for the downloaded files.
The script will not create this folder, so make sure it exists.
'''
save_path = '~/Downloads/yt-rips' 
is_downloading = False
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
current_download_process = None
should_stop_download = False

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "👋 Hello! I’m <b>MinoDownloader</b>, your very own YouTube Video Downloader bot.\n\n"
        "• Use <code>/help</code> to <b>see what I can do</b>.\n"
        "• Use <code>/dl &lt;YouTube URL&gt;</code> to <b>download audio</b>.\n"
        "• Use <code>/myid</code> to <b>get your Telegram user ID</b>.\n"
        "• Use <code>/skip</code> to <b>skip the current download and continue to the next</b>.\n"
        "• Use <code>/stop</code> to <b>stop the current download</b>.\n"
        "• Use <code>/current</code> to <b>show the currently downloading item (with preview)</b>.\n"
        "• Use <code>/queue</code> to <b>check the download queue status</b>.\n"
        "• Use <code>/purge</code> to <b>clear</b> the download queue (Admins Only).\n"
        "• Use <code>/test</code> to <b>test</b> the bot with a sample URL (Admins Only).\n\n"
        "📁 <b>Downloaded files are saved in:</b>\n"
        "<b>• Android:</b> <code>Downloads/yt-rips/</code>\n"
        "<b>• iOS:</b> <i>Receive the file in Telegram and tap 'Save to Files' to store it on your device.</i>\n"
        "<b>• Windows(or WSL):</b> <code>C:\\Users\\&lt;your-username&gt;\\Downloads\\yt-rips\\</code>\n"
        "<b>• MacOS:</b> <code>~/Downloads/yt-rips/</code>\n"
        "<b>• Linux:</b> <code>~/Downloads/yt-rips/</code>\n"
        "Open this folder to find your MP3 files!"
    )
    await update.message.reply_text(message, parse_mode='HTML')

import os
import asyncio

async def delete_file_later(file_path, delay=600):
    await asyncio.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    yt_url = " ".join(context.args)
    if not yt_url:
        await update.message.reply_text('Please provide a YouTube URL.')
        return

    user_id = update.effective_user.id

    # -- Your download logic here --
    # Let's assume you have a function that downloads and returns the file path
    # Example: file_path = await download_video(yt_url, user_id)
    # For demonstration, we'll use a placeholder path:
    import yt_dlp

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    yt_url = " ".join(context.args)
    if not yt_url:
        await update.message.reply_text('Please provide a YouTube URL.')
        return

    user_id = update.effective_user.id

    # --- Download logic START ---
    # Set output folder and filename
    output_dir = "/storage/emulated/0/Download/yt-rips"
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, f"{user_id}_%(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }

    file_path = None
    try:
         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             info = ydl.extract_info(yt_url, download=True)
             file_path = ydl.prepare_filename(info)
         if file_path.endswith('.webm') and os.path.exists(file_path.replace('.webm', '.mp4')):
             file_path = file_path.replace('.webm', '.mp4')
    except Exception as e:
         await update.message.reply_text(f"❌ Download failed: {e}")
         return

# Send the file to the user
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as file:
           await update.message.reply_document(
               document=file,
               caption="⚠️ This file will be deleted in 10 minutes. Please forward or save it if needed."
           )
        asyncio.create_task(delete_file_later(file_path, delay=600))
    else:
        await update.message.reply_text("Sorry, the file could not be found after download.")


#    user_id = update.effective_user.id
#    if user_id not in admins and user_id not in users:
#    await update.message.reply_text('Sorry, you are not authorized to use this command.')
#    return
    yt_url = " ".join(context.args)
    if not yt_url:
        await update.message.reply_text('Please provide a YouTube URL.')
        return
    user_id = update.effective_user.id
    is_playlist = await download_queue.handle_playlist(yt_url, user_id, update)
    if not is_playlist:
        await download_queue.add_to_queue(yt_url, user_id, update)


async def url_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#   user_id = update.effective_user.id
#   if user_id not in admins and user_id not in users:
#   await update.message.reply_text('Sorry, you are not authorized to use this command.')
#   return
    yt_url = 'https://www.youtube.com/playlist?list=PLXfw2d8gdlIax3QQHbl5uCB54YWe6qyIN'
    is_playlist = await download_queue.handle_playlist(yt_url, user_id, update)
    if not is_playlist:
        await download_queue.add_to_queue(yt_url, user_id, update)

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    await update.message.reply_text(f'Your User ID: {user_id}\nYour Username: @{username}')

async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands_text = """
*/help* - Show this help message
*/hello* - Greet the bot
*/myid* - Get your user ID (send to admin to be allowed to download)
*/dl <url>* - Download a YouTube video (or playlist)
*/skip* - Skip the current download and continue to the next
*/stop* - Stop the current download
*/current* - Show the currently downloading item (with preview)
*/queue* - Check the download queue status
*/purge* - Clear the download queue (admins only)
*/test* - Test the bot with a sample URL (admins only)"""
    await update.message.reply_text(commands_text, parse_mode='Markdown')

def main():
    global admins, users
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, 'authorised_users.yml')

    try:
        with open(config_file, 'r') as file:
          data = yaml.safe_load(file)
          admins = data['admins']
          users = data['users']
          print('Admins:', admins)
          print('Users:', users)
    except FileNotFoundError:
      print("YAML file not found. Rename 'authorised_users_example.yml' and fill the required data.")
      sys.exit(1)

    app = ApplicationBuilder().token(TG_TOKEN).build()
    
    download_queue.queue_init({
        'save_path': save_path,
        'executor': executor,
        'admins': admins,
        'users': users,
        'token': TG_TOKEN,
        'should_stop_download': should_stop_download,
        'current_download_process': current_download_process
    })


    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("help", commands))
    app.add_handler(CommandHandler("myid", get_id))
    app.add_handler(CommandHandler("dl", url))
    app.add_handler(CommandHandler("queue", download_queue.queue_status))
    app.add_handler(CommandHandler("current", download_queue.current_download))
    app.add_handler(CommandHandler("purge", download_queue.purge_queue))
    app.add_handler(CommandHandler("stop", download_queue.stop_download))
    app.add_handler(CommandHandler("skip", download_queue.skip_download))
    app.add_handler(CommandHandler("test", url_test))
    app.add_handler(CommandHandler("start", start))

    app.job_queue.run_once(lambda _: download_queue.recover_queue(), 1)
    app.run_polling()

if __name__ == '__main__':
    main()
