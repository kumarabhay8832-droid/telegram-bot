import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ✅ TOKEN (Railway se aayega)
import os
TOKEN = "8618508924:AAFB18IXWHGDJlkVjTEZYPIlTCVysiN9TRw"

# 📦 Data
users_gender = {}
waiting_male = []
waiting_female = []
connections = {}


# 🟢 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👦 Male", callback_data="male")],
        [InlineKeyboardButton("👧 Female", callback_data="female")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome!\nSelect your gender 👇",
        reply_markup=reply_markup
    )


# 🟢 BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "male":
        users_gender[user_id] = "male"
        await query.message.reply_text("✅ Male selected\nUse /find")

    elif query.data == "female":
        users_gender[user_id] = "female"
        await query.message.reply_text("✅ Female selected\nUse /find")

    elif query.data == "find":
        gender = users_gender.get(user_id)

        if not gender:
            await query.message.reply_text("⚠️ First select gender /start")
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


# 🟢 FIND COMMAND
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔍 Find Partner", callback_data="find")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Click below 👇", reply_markup=reply_markup)


# 🟢 MESSAGE FORWARD
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in connections:
        partner = connections[user_id]
        await context.bot.send_message(chat_id=partner, text=update.message.text)
    else:
        await update.message.reply_text("⚠️ Not connected. Use /find")


# 🟢 MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
