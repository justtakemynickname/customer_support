import logging
from telegram import Update, InputFile, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from text_module import handle_text_query
from vision_module import handle_image
from audio_module import handle_audio
import os

# Define your bot token here
TOKEN = '7986591464:AAFZU3D49y5k2m4aYZwxju_2z7Ox2wSiFak'

# Initialize the bot with the token
bot = Bot(token=TOKEN)

# Get bot details to confirm it's working
print(bot.get_me())

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm here to assist you. Send me text, images, or audio.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = handle_text_query(text)
    await update.message.reply_text(response)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = os.path.join('downloads', f'{photo_file.file_unique_id}.jpg')
    await photo_file.download(photo_path)
    response = handle_image(photo_path)
    await update.message.reply_text(response)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()
    audio_path = os.path.join('downloads', f'{voice_file.file_unique_id}.ogg')
    await voice_file.download(audio_path)
    response = handle_audio(audio_path)
    await update.message.reply_text(response)

if __name__ == '__main__':
    # Use the token as a string directly
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()
