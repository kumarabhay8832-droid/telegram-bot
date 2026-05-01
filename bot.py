import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 🔑 TOKEN (Railway env variable se)
TOKEN = os.getenv("BOT_TOKEN")

# 📦 Data storage
users_gender = {}        # user_id : gender
waiting_male = []        # male queue
waiting_female = []      # female queue
connections = {}         # active chats


# 🟢 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👦 Male", callback_data="male")],
        [InlineKeyboardButton("👧 Female", callback_data="female")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome!\n\nSelect your gender 👇",
        reply_markup=reply_markup
    )


# 🟢 BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # 👉 Gender select
    if query.data == "male":
        users_gender[user_id] = "male"
        await query.message.reply_text("✅ You selected Male\nClick /find to start")

    elif query.data == "female":
        users_gender[user_id] = "female"
        await query.message.reply_text("✅ You selected Female\nClick /find to start")

    # 👉 Find partner
    elif query.data == "find":
        gender = users_gender.get(user_id)

        if not gender:
            await query.message.reply_text("⚠️ Please select gender first (/start)")
            return

        if gender == "male":
            if waiting_female:
                partner = waiting_female.pop(0)
                connections[user_id] = partner
                connections[partner] = user_id

                await context.bot.send_message(partner, "💬 Connected!")
                await query.message.reply_text("💬 Connected!")
            else:
                waiting_male.append(user_id)
                await query.message.reply_text("⏳ Waiting for female...")

        elif gender == "female":
            if waiting_male:
                partner = waiting_male.pop(0)
                connections[user_id] = partner
                connections[partner] = user_id

                await context.bot.send_message(partner, "💬 Connected!")
                await query.message.reply_text("💬 Connected!")
            else:
                waiting_female.append(user_id)
                await query.message.reply_text("⏳ Waiting for male...")


# 🟢 FIND COMMAND (button ke bina bhi kaam kare)
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    keyboard = [
        [InlineKeyboardButton("🔍 Find Partner", callback_data="find")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Click below to find partner 👇", reply_markup=reply_markup)


# 🟢 MESSAGE FORWARD
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in connections:
        partner = connections[user_id]
        await context.bot.send_message(chat_id=partner, text=update.message.text)
    else:
        await update.message.reply_text("⚠️ Not connected. Use /find")


# 🟢 MAIN FUNCTION
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    print("Bot is running...")
    app.run_polling()


# ▶️ RUN
if __name__ == "__main__":
    main()
