# bot/handlers/common_helpers.py

from telegram import Update
from telegram.ext import ContextTypes

async def feature_in_development(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заглушка для функций, которые в разработке.
    """
    await update.message.reply_text("⏳ Эта функция находится в разработке. Пожалуйста, зайдите позже.")
