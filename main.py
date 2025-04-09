main.py

import os import subprocess import tempfile from telegram import Update from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE): doc = update.message.document if not doc.file_name.endswith(".txt"): await update.message.reply_text("Please send a .txt file containing the video URL and DRM keys.") return

telegram_file = await doc.get_file()
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
    await telegram_file.download_to_drive(tmp.name)
    tmp_path = tmp.name

await update.message.reply_text("Downloaded the file. Now processing...")

with open(tmp_path, 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

if len(lines) < 2:
    await update.message.reply_text("Your file must contain at least one link and one key.")
    return

video_url = lines[0]
keys = ["--key"] + [key for key in lines[1:] if ':' in key]

# Download encrypted file
enc_file = "encrypted.mp4"
subprocess.run(["ffmpeg", "-i", video_url, "-c", "copy", enc_file], check=True)

# Decrypt using mp4decrypt
dec_file = "decrypted.mp4"
decrypt_cmd = ["mp4decrypt"] + keys + [enc_file, dec_file]
subprocess.run(decrypt_cmd, check=True)

# Send back the file
await update.message.reply_video(video=dec_file, caption="Here's your decrypted video.")

os.remove(tmp_path)
os.remove(enc_file)
os.remove(dec_file)

if name == 'main': app = ApplicationBuilder().token(TOKEN).build() doc_handler = MessageHandler(filters.Document.ALL, handle_document) app.add_handler(doc_handler) app.run_polling()

