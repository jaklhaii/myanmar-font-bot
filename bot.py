#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Professional Myanmar Font Converter & Document Processing Bot
- Pyidaungsu Font Converter
- Advanced PDF Text Cleaning & Reordering
- PowerPoint (.pptx) Slide Image Extractor (Pure Python / Pillow)
"""

import logging
import os
import sys
import tempfile
import unicodedata
import re
import converter
from pypdf import PdfReader
from pptx import Presentation
from PIL import Image, ImageDraw, ImageFont
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


def clean_myanmar_pdf_text(text: str) -> str:
    """Clean and reorder Myanmar text extracted from PDFs where combining vowels/tones might be displaced."""
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFC', text)
    
    # Fix common PDF extraction issues:
    # Removed manual swapping of ေ (U+1031) as it's handled by the converter
    # and to maintain standard Unicode logical order.
    
    # Apply standard converter to pyidaungsu
    converted = converter.to_pyidaungsu(text)
    return converted


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a stunning pro-style welcome message."""
    user = update.effective_user
    welcome_text = (
        f"✨ မင်္ဂလာပါ {user.first_name} ခင်ဗျာ ✨\n\n"
        "──────────────────────────────\n"
        "🎯 Pyidaungsu Font & Document Bot Pro\n"
        "──────────────────────────────\n\n"
        "📌 လုပ်ဆောင်ချက်များ:\n"
        "၁။ Font Converter: မည်သည့် မြန်မာစာသားကိုမဆို Pyidaungsu Unicode သို့ ပြောင်းပေးခြင်း။\n"
        "၂။ PDF Text Extractor: PDF ဖိုင်ပို့ပါက စာများဖတ်၍ Pyidaungsu ဖြင့် Quote ပုံစံဖြင့် ပြန်ပို့ပေးခြင်း။\n"
        "၃။ PPTX to Images: PowerPoint ဖိုင်ပို့ပါက Slide တစ်ခုချင်းစီကို ပုံများအဖြစ် ပြန်ပို့ပေးခြင်း။\n\n"
        "💡 အသုံးပြုရန် ဖိုင် သို့မဟုတ် စာသားများကို Bot ထံ တိုက်ရိုက် ပို့ပေးပါ။"
    )

    keyboard = [
        [InlineKeyboardButton("📖 အသုံးပြုပုံ အသေးစိတ်", callback_data="help")],
        [InlineKeyboardButton("💎 Pro Features", callback_data="features")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provide guide."""
    help_text = (
        "📖 အသုံးပြုပုံ လမ်းညွှန်\n\n"
        "• စာသားများ: ဇော်ဂျီ သို့မဟုတ် ဖောင့်မမှန်သည်များကို ပို့ပါက Pyidaungsu သို့ ပြောင်းပေးမည်။\n"
        "• PDF ဖိုင်များ: PDF ပို့ပါက စာသားများကို Pyidaungsu ဖောင့်ဖြင့် Quote ပုံစံ ပို့ပေးမည်။\n"
        "• PPTX ဖိုင်များ: PowerPoint ဖိုင်ပို့ပါက Slide တစ်ခုချင်းစီကို ပုံ (Images) အဖြစ် ပို့ပေးမည်။"
    )
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ ပင်မမီနူးသို့", callback_data="main_menu")]]
        await query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(help_text)


async def features_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Highlight features."""
    features_text = (
        "💎 Pro Features များနှင့် အားသာချက်များ\n\n"
        "• Smart Font Detection & Conversion\n"
        "• PDF Text Extraction with Clean Quotes\n"
        "• PowerPoint Slide-to-Image Rendering"
    )
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ ပင်မမီနူးသို့", callback_data="main_menu")]]
        await query.message.edit_text(features_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries."""
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await help_command(update, context)
    elif query.data == "features":
        await features_command(update, context)
    elif query.data == "main_menu":
        await start_command(update, context)


async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process incoming messages and return clean converted text in quotes."""
    if not update.message or not update.message.text:
        return

    raw_text = update.message.text

    try:
        converted_text = clean_myanmar_pdf_text(raw_text)
        quoted_text = f"> {converted_text.replace(chr(10), chr(10) + '> ')}"
        await update.message.reply_text(quoted_text)
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        await update.message.reply_text("> ❌ စာသားပြောင်းလဲရာတွင် အမှားရှိနေပါသည်။ ထပ်မံကြိုးစားပါ။")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle PDF and PowerPoint (.pptx) document uploads robustly."""
    message = update.message
    if not message or not message.document:
        return

    doc = message.document
    file_name = doc.file_name.lower()
    
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
                        cleaned_text = clean_myanmar_pdf_text(text)
                        full_text += f"--- Page {idx + 1} ---\n{cleaned_text}\n\n"
                
                if not full_text.strip():
                    full_text = "⚠️ ဤ PDF ဖိုင်ထဲတွင် ကောက်ယူနိုင်သော စာသား (Text) မတွေ့ရှိပါ။ (ပုံ သို့မဟုတ် Scanned PDF ဖြစ်နိုင်ပါသည်။)"
                
                quoted_full_text = f"> {full_text.replace(chr(10), chr(10) + '> ')}"

                max_length = 3800
                for i in range(0, len(quoted_full_text), max_length):
                    await message.reply_text(quoted_full_text[i:i + max_length])
                await status_msg.delete()

            # 2. Handle PowerPoint Files (.pptx) via python-pptx rendering
            elif file_name.endswith('.pptx'):
                prs = Presentation(input_path)
                slides_count = len(prs.slides)
                await status_msg.edit_text(f"📸 PowerPoint Slides ({slides_count} slides) များကို ပုံများအဖြစ် ပြောင်းလဲပြီး ပို့ဆောင်နေပါပြီ...")

                # Load Font for Myanmar Rendering
                font_path = "Pyidaungsu.ttf"
                try:
                    font_title = ImageFont.truetype(font_path, 40)
                    font_body = ImageFont.truetype(font_path, 25)
                except:
                    font_title = None
                    font_body = None

                for idx, slide in enumerate(prs.slides):
                    img = Image.new('RGB', (1280, 720), color=(245, 247, 250))
                    draw = ImageDraw.Draw(img)
                    
                    slide_text_lines = []
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for paragraph in shape.text_frame.paragraphs:
                                p_text = paragraph.text.strip()
                                if p_text:
                                    slide_text_lines.append(clean_myanmar_pdf_text(p_text))

                    draw.rectangle([0, 0, 1280, 100], fill=(24, 43, 73))
                    draw.text((50, 35), f"Slide {idx + 1} / {slides_count}", fill=(255, 255, 255), font=font_title)
                    
                    y_offset = 140
                    for line in slide_text_lines[:15]:
                        draw.text((60, y_offset), line[:80], fill=(30, 30, 30), font=font_body)
                        y_offset += 35

                    img_path = os.path.join(temp_dir, f"slide_{idx + 1}.png")
                    img.save(img_path, 'PNG')

                    with open(img_path, 'rb') as photo:
                        caption_text = f"> 📄 Slide {idx + 1} / {slides_count}"
                        await message.reply_photo(photo=photo, caption=caption_text)
                
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
