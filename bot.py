#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Professional Myanmar Font Converter Bot (Refined Pro Style Edition)
Gorgeous UI combined with clean, crystal-clear, and structured text.
"""

import logging
import os
import sys
import converter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Configure logging format
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Retrieve Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or "8183997269:AAHF5VgSgR7TJhC0HX9QgPCs74olBmoh2eA"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a stunning pro-style welcome message with crystal-clear explanations."""
    user = update.effective_user
    welcome_text = (
        f"✨ **မင်္ဂလာပါ {user.first_name} ခင်ဗျာ** ✨\n\n"
        "──────────────────────────────\n"
        "🎯 **Pyidaungsu Font Converter Pro Bot**\n"
        "──────────────────────────────\n\n"
        "📌 **လုပ်ဆောင်ချက်:**\n"
        "PowerPoint တွင် စာသားများ ဖောင့်မကွဲစေရန် မည်သည့် မြန်မာစာသားကိုမဆို **Pyidaungsu Unicode** သို့ အလိုအလျောက် ပြောင်းပေးပါသည်။\n\n"
        "💡 **အသုံးပြုပုံ:**\n"
        "စာသားများကို ဤ Bot ထံသို့ တိုက်ရိုက် ပို့ပေးရုံပါပဲ။ စက္ကန့်ပိုင်းအတွင်း အသင့်သုံးစာသားကို ပြန်ပို့ပေးပါမည်။\n\n"
        "👇 အောက်ပါခလုတ်များကို နှိပ်၍ လေ့လာနိုင်ပါသည်။"
    )

    keyboard = [
        [InlineKeyboardButton("📖 အသုံးပြုပုံ အသေးစိတ်", callback_data="help")],
        [InlineKeyboardButton("💎 Pro Features", callback_data="features")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provide a clean, structured guide for PowerPoint users."""
    help_text = (
        "📖 **PowerPoint တွင် အသုံးပြုရန် လမ်းညွှန်**\n\n"
        "၁။ ဖောင့်မမှန်သော (သို့) ဇော်ဂျီစာသားများကို Bot ထံ ပို့ပါ။\n"
        "၂။ Bot မှ ပြောင်းပေးလိုက်သော စာသားကို Copy ကူးပါ။\n"
        "၃။ PowerPoint တွင် **Pyidaungsu** ဖောင့်ကို ရွေးချယ်ပြီး Paste လုပ်ပါ။\n\n"
        "✨ *ယခုအခါ စာလုံးများ လုံးဝ မကွဲတော့ဘဲ သပ်ရပ်စွာ ပေါ်လာမည် ဖြစ်ပါသည်။*"
    )
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ ပင်မမီနူးသို့", callback_data="main_menu")]]
        await query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")


async def features_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Highlight professional features clearly."""
    features_text = (
        "💎 **Pro Features များနှင့် အားသာချက်များ**\n\n"
        "• **Smart Detection:** ဇော်ဂျီနှင့် ယူနီကုတ်ကို အလိုအလျောက် ခွဲခြားပေးခြင်း။\n"
        "• **Lightning Fast:** စက္ကန့်ပိုင်းအတွင်း အမြန်ဆုံး ပြောင်းလဲပေးခြင်း။\n"
        "• **Error Free:** PowerPoint တင်ရာတွင် ဖောင့်ပြဿနာ လုံးဝ ကင်းဝေးစေခြင်း။"
    )
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ ပင်မမီနူးသို့", callback_data="main_menu")]]
        await query.message.edit_text(features_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries smoothly."""
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await help_command(update, context)
    elif query.data == "features":
        await features_command(update, context)
    elif query.data == "main_menu":
        await start_command(update, context)


async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process incoming messages and return clean converted text."""
    if not update.message or not update.message.text:
        return

    raw_text = update.message.text

    try:
        converted_text = converter.to_pyidaungsu(raw_text)
        await update.message.reply_text(converted_text)
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        await update.message.reply_text("❌ စာသားပြောင်းလဲရာတွင် အမှားရှိနေပါသည်။ ထပ်မံကြိုးစားပါ။")


def main() -> None:
    """Initialize and run the Refined Pro-Style Bot."""
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.critical("Bot Token is not configured.")
        sys.exit(1)

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_incoming_message))

    logger.info("Refined Pro-Style Font Converter Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
