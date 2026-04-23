import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8618508924:AAFB18IXWHGDJlkVjTEZYPIlTCVysiN9TRw"

waiting_user = None
active_chats = {}

logging.basicConfig(level=logging.INFO)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Find Partner", callback_data="find")],
        [InlineKeyboardButton("⏭ Next", callback_data="next")],
        [InlineKeyboardButton("⛔ Stop", callback_data="stop")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome!\n\nClick 'Find Partner' to start chatting with strangers.",
        reply_markup=reply_markup,
    )

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_user
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    # FIND PARTNER
    if query.data == "find":
        if user_id in active_chats:
            await query.message.reply_text("⚠️ You are already in a chat.")
            return

        if waiting_user is None:
            waiting_user = user_id
            await query.message.reply_text("⏳ Waiting for a partner...")
        else:
            partner = waiting_user
            waiting_user = None

            active_chats[user_id] = partner
            active_chats[partner] = user_id

            await context.bot.send_message(user_id, "✅ Connected! Say hi 👋")
            await context.bot.send_message(partner, "✅ Connected! Say hi 👋")

    # NEXT PARTNER
    elif query.data == "next":
        await disconnect(user_id, context)
        await button(update, context)

    # STOP CHAT
    elif query.data == "stop":
        await disconnect(user_id, context)
        await query.message.reply_text("⛔ Chat stopped.")

# Disconnect users
async def disconnect(user_id, context):
    if user_id in active_chats:
        partner = active_chats[user_id]

        await context.bot.send_message(partner, "❌ Partner left the chat.")

        del active_chats[partner]
        del active_chats[user_id]

# Message handler (forward messages)
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in active_chats:
        partner = active_chats[user_id]
        await context.bot.send_message(partner, update.message.text)
    else:
        await update.message.reply_text("⚠️ Click 'Find Partner' first.")

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
