#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Professional Myanmar Font Converter & Document Processing Bot
- Pyidaungsu Font Converter
- PDF Text Extraction
- PowerPoint (.pptx) to Slide Images Converter
"""

import logging
import os
import sys
import subprocess
import tempfile
import converter
from pypdf import PdfReader
from pdf2image import convert_from_path
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
        "🎯 **Pyidaungsu Font & Document Bot Pro**\n"
        "──────────────────────────────\n\n"
        "📌 **လုပ်ဆောင်ချက်များ:**\n"
        "၁။ **Font Converter:** မည်သည့် မြန်မာစာသားကိုမဆို Pyidaungsu Unicode သို့ ပြောင်းပေးခြင်း။\n"
        "၂။ **PDF Text Extractor:** PDF ဖိုင်ပို့ပါက အတွင်းပါစာများ အကုန်ထုတ်ပေးခြင်း။\n"
        "၃။ **PPTX to Images:** PowerPoint ဖိုင်ပို့ပါက Slide တစ်ခုချင်းစီကို ပုံများအဖြစ် ပြန်ပို့ပေးခြင်း။\n\n"
        "💡 *အသုံးပြုရန် ဖိုင် သို့မဟုတ် စာသားများကို Bot ထံ တိုက်ရိုက် ပို့ပေးပါ။*"
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
    """Provide a clean, structured guide."""
    help_text = (
        "📖 **အသုံးပြုပုံ လမ်းညွှန်**\n\n"
        "• **စာသားများ:** ဇော်ဂျီ သို့မဟုတ် ဖောင့်မမှန်သည်များကို ပို့ပါက Pyidaungsu သို့ ပြောင်းပေးမည်။\n"
        "• **PDF ဖိုင်များ:** PDF ပို့ပါက စာသားများကို ဖတ်၍ ပြန်ပို့ပေးမည်။\n"
        "• **PPTX ဖိုင်များ:** PowerPoint ဖိုင်ပို့ပါက Slide တစ်ခုချင်းစီကို ပုံ (Images) အဖြစ် ပြန်ပို့ပေးမည်။"
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
        "• **Smart Font Detection & Conversion**\n"
        "• **PDF Text Extraction Engine**\n"
        "• **PowerPoint Slide-to-Image Rendering**"
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


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle PDF and PowerPoint (.pptx) document uploads."""
    message = update.message
    if not message or not message.document:
        return

    doc = message.document
    file_name = doc.file_name.lower()
    
    # Acknowledge receipt
    status_msg = await message.reply_text("⏳ ဖိုင်ကို လက်ခံရရှိပါပြီ။ ဆောင်ရွက်နေပါသည်...")

    try:
        file_obj = await doc.get_file()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, doc.file_name)
            await file_obj.download_to_drive(input_path)

            # 1. Handle PDF Files
            if file_name.endswith('.pdf'):
                reader = PdfReader(input_path)
                full_text = ""
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        full_text += f"--- Page {idx + 1} ---\n{text}\n\n"
                
                if not full_text.strip():
                    full_text = "⚠️ ဤ PDF ဖိုင်ထဲတွင် ကောက်ယူနိုင်သော စာသား (Text) မတွေ့ရှိပါ။ (ပုံစံ သို့မဟုတ် Scanned PDF ဖြစ်နိုင်ပါသည်။)"
                
                # Split message if too long (Telegram limit 4096 chars)
                max_length = 4000
                for i in range(0, len(full_text), max_length):
                    await message.reply_text(full_text[i:i + max_length])
                await status_msg.delete()

            # 2. Handle PowerPoint Files (.pptx)
            elif file_name.endswith('.pptx'):
                # Convert PPTX to PDF using libreoffice
                cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', input_path, '--outdir', temp_dir]
                subprocess.run(cmd, check=True)
                
                base_name = os.path.splitext(doc.file_name)[0]
                pdf_path = os.path.join(temp_dir, f"{base_name}.pdf")
                if not os.path.exists(pdf_path):
                    # fallback search
                    for f in os.listdir(temp_dir):
                        if f.endswith('.pdf'):
                            pdf_path = os.path.join(temp_dir, f)
                            break

                # Convert PDF pages to images
                images = convert_from_path(pdf_path)
                await status_msg.edit_text(f"📸 PowerPoint Slides ({len(images)} slides) များကို ပုံများအဖြစ် ပြောင်းလဲပြီး ပို့ဆောင်နေပါပြီ...")

                for idx, image in enumerate(images):
                    img_path = os.path.join(temp_dir, f"slide_{idx + 1}.png")
                    image.save(img_path, 'PNG')
                    with open(img_path, 'rb') as photo:
                        await message.reply_photo(photo=photo, caption=f"📄 Slide {idx + 1} / {len(images)}")
                
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ ကျေးဇူးပြု၍ **PDF** သို့မဟုတ် **PowerPoint (.pptx)** ဖိုင်များကိုသာ ပို့ပေးပါ။")

    except Exception as e:
        logger.error(f"Document processing error: {e}")
        await status_msg.edit_text(f"❌ ဖိုင်လုပ်ဆောင်ရာတွင် အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {str(e)}")


def main() -> None:
    """Initialize and run the Bot."""
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.critical("Bot Token is not configured.")
        sys.exit(1)

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_incoming_message))

    logger.info("Enhanced Document Processing Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
