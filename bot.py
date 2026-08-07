#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Professional Myanmar Font Converter & Document Processing Bot
- Smart Zawgyi/Unicode Detection
- Tesseract OCR for PDF (Fixes broken font issues)
- Reliable PDF Text Extraction & Conversion
- Interactive PPTX/PDF Flow
"""

import logging
import os
import sys
import tempfile
import unicodedata
import re
import shutil
import converter
import rabbit
import pytesseract
from pdf2image import convert_from_path
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

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Retrieve Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or "8183997269:AAHF5VgSgR7TJhC0HX9QgPCs74olBmoh2eA"
FONT_PATH = "Pyidaungsu.ttf"

def is_zawgyi(text: str) -> bool:
    """Robust heuristic to detect if text is Zawgyi encoded."""
    if not text:
        return False
    zg_chars = r'[\u107e-\u1084\u1088\u1089\u1090\u1091\u1092\u1097]'
    if re.search(zg_chars, text):
        return True
    if re.search(r'[\u1031\u103c][\u1000-\u1021]', text):
        return True
    return False

def clean_myanmar_text(text: str) -> str:
    """Clean and convert Myanmar text with smart detection."""
    if not text:
        return ""
    
    # Step 1: PUA cleaning
    pua_map = {
        '\uE107': '\u1014', #  -> န
        '\uE100': '\u1000',
        '\uE101': '\u1001',
    }
    for k, v in pua_map.items():
        text = text.replace(k, v)
    text = re.sub(r'[\uE000-\uF8FF]', '', text)
    
    # Step 2: Zawgyi to Unicode
    if is_zawgyi(text):
        try:
            text = rabbit.zg2uni(text)
        except Exception as e:
            logger.error(f"Rabbit conversion failed: {e}")
    
    # Step 3: Standardize and Normalize
    text = unicodedata.normalize('NFC', text)
    
    # Step 4: Final pass for Pyidaungsu integrity
    try:
        text = converter.to_pyidaungsu(text)
    except Exception as e:
        logger.error(f"Converter failed: {e}")
        
    return text

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message."""
    user = update.effective_user
    welcome_text = (
        f"✨ မင်္ဂလာပါ {user.first_name} ခင်ဗျာ ✨\n\n"
        "──────────────────────────────\n"
        "🎯 Myanmar Font Bot Pro (OCR Edition)\n"
        "──────────────────────────────\n\n"
        "📌 လုပ်ဆောင်ချက်များ:\n"
        "၁။ Font Converter: ဇော်ဂျီနှင့် ဖောင့်မမှန်သည်များကို Unicode သို့ အလိုအလျောက် ပြောင်းပေးခြင်း။\n"
        "၂။ PDF OCR: PDF ဖောင့်လွဲနေပါက OCR စနစ်ဖြင့် ပုံဖတ်၍ စာသားများ ထုတ်ယူပေးခြင်း။\n"
        "၃။ PPTX to Images: PowerPoint ကို ပုံများအဖြစ် ပြောင်းပေးခြင်း။\n\n"
        "💡 အသုံးပြုရန် ဖိုင် သို့မဟုတ် စာသားများကို ပို့ပေးပါ။"
    )

    keyboard = [
        [InlineKeyboardButton("📖 အသုံးပြုပုံ လမ်းညွှန်", callback_data="help")],
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
        "• စာသားများ: ပို့လိုက်သော စာသားများကို Unicode အဖြစ် ပြောင်းလဲပေးမည်။\n"
        "• PDF ဖိုင်များ: OCR စနစ်သုံးထားသောကြောင့် ဖောင့်လွဲနေသော PDF များမှ စာသားများကို အတိကျဆုံး ထုတ်ယူပေးနိုင်ပါသည်။\n"
        "• PPTX ဖိုင်များ: ပထမစာမျက်နှာကို အရင်ပြမည်ဖြစ်ပြီး ခလုတ်များနှိပ်၍ ဆက်လက်ထုတ်ယူနိုင်ပါသည်။"
    )
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ ပင်မမီနူးသို့", callback_data="main_menu")]]
        await query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def features_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Highlight features."""
    features_text = (
        "💎 Pro Features\n\n"
        "• Tesseract OCR Integration (Myanmar Language Support)\n"
        "• Smart Zawgyi/Unicode Auto-Detection\n"
        "• High Quality Font Rendering\n"
        "• Interactive Document Flow"
    )
    query = update.callback_query
    if query:
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ ပင်မမီနူးသို့", callback_data="main_menu")]]
        await query.message.edit_text(features_text, reply_markup=InlineKeyboardMarkup(keyboard))

def render_pptx_slide(input_path, slide_idx, total_slides):
    """Render a single PPTX slide to an image."""
    prs = Presentation(input_path)
    if slide_idx >= len(prs.slides):
        return None
    slide = prs.slides[slide_idx]
    img = Image.new('RGB', (1280, 720), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype(FONT_PATH, 42)
        font_body = ImageFont.truetype(FONT_PATH, 30)
    except:
        font_title = font_body = None
    slide_text_lines = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                p_text = paragraph.text.strip()
                if p_text:
                    slide_text_lines.append(clean_myanmar_text(p_text))
    draw.rectangle([0, 0, 1280, 100], fill=(24, 43, 73))
    draw.text((50, 30), f"Slide {slide_idx + 1} / {total_slides}", fill=(255, 255, 255), font=font_title)
    y_offset = 140
    for line in slide_text_lines[:15]:
        draw.text((60, y_offset), line[:70], fill=(30, 30, 30), font=font_body)
        y_offset += 45
    temp_img_path = os.path.join(tempfile.gettempdir(), f"slide_render_{slide_idx}.png")
    img.save(temp_img_path, 'PNG')
    return temp_img_path

def extract_pdf_page_ocr(input_path, page_idx):
    """Extract text from a PDF page using Tesseract OCR."""
    try:
        # Convert specific page to image
        images = convert_from_path(input_path, first_page=page_idx+1, last_page=page_idx+1, dpi=300)
        if not images:
            return f"--- Page {page_idx + 1} ---\n(ပုံအဖြစ်ပြောင်းလဲ၍မရပါ)"
        
        # Use Tesseract OCR with Myanmar and English languages
        text = pytesseract.image_to_string(images[0], lang='mya+eng')
        if text.strip():
            cleaned = clean_myanmar_text(text)
            return f"--- Page {page_idx + 1} (OCR) ---\n{cleaned}"
        
        # Fallback to normal extraction if OCR returns empty
        reader = PdfReader(input_path)
        text = reader.pages[page_idx].extract_text()
        if text:
            return f"--- Page {page_idx + 1} (Fallback) ---\n{clean_myanmar_text(text)}"
            
    except Exception as e:
        logger.error(f"OCR Error on page {page_idx}: {e}")
        error_msg = str(e)
        if "poppler" in error_msg.lower():
            return f"--- Page {page_idx + 1} ---\n(စနစ်အတွင်း Poppler တပ်ဆင်မှု လိုအပ်နေပါသည်။ ခဏစောင့်ပေးပါ။)"
        return f"--- Page {page_idx + 1} ---\n(OCR အမှား: {error_msg})"
    
    return f"--- Page {page_idx + 1} ---\n(စာသားမတွေ့ရှိပါ)"

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document upload."""
    message = update.message
    if not message or not message.document:
        return
    doc = message.document
    file_name = doc.file_name.lower()
    if not (file_name.endswith('.pdf') or file_name.endswith('.pptx')):
        await message.reply_text("❌ ကျေးဇူးပြု၍ **PDF** သို့မဟုတ် **PowerPoint (.pptx)** ဖိုင်များကိုသာ ပို့ပေးပါ။")
        return
    status_msg = await message.reply_text("⏳ ဖိုင်ကို လက်ခံရရှိပါပြီ။ OCR စနစ်ဖြင့် စစ်ဆေးနေပါသည်...")
    try:
        file_obj = await doc.get_file()
        user_dir = os.path.join(tempfile.gettempdir(), f"user_{update.effective_user.id}")
        os.makedirs(user_dir, exist_ok=True)
        input_path = os.path.join(user_dir, doc.file_name)
        await file_obj.download_to_drive(input_path)
        doc_type = 'pdf' if file_name.endswith('.pdf') else 'pptx'
        if doc_type == 'pdf':
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
        else:
            prs = Presentation(input_path)
            total_pages = len(prs.slides)
        context.user_data['current_doc'] = {
            'path': input_path,
            'type': doc_type,
            'total': total_pages,
            'current_idx': 0
        }
        await status_msg.delete()
        await send_next_part(update, context)
    except Exception as e:
        logger.error(f"Upload error: {e}")
        await message.reply_text(f"❌ အမှားအယွင်း ဖြစ်သွားပါသည်: {str(e)}")

async def send_next_part(update: Update, context: ContextTypes.DEFAULT_TYPE, send_all=False) -> None:
    """Send pages."""
    doc_info = context.user_data.get('current_doc')
    if not doc_info: return
    idx = doc_info['current_idx']
    total = doc_info['total']
    path = doc_info['path']
    dtype = doc_info['type']
    while idx < total:
        if dtype == 'pdf':
            content = extract_pdf_page_ocr(path, idx)
            quoted = f"> {content.replace(chr(10), chr(10) + '> ')}"
            if update.callback_query:
                await update.callback_query.message.reply_text(quoted)
            else:
                await update.message.reply_text(quoted)
        else:
            img_path = render_pptx_slide(path, idx, total)
            caption = f"> 📄 Slide {idx + 1} / {total}"
            with open(img_path, 'rb') as photo:
                if update.callback_query:
                    await update.callback_query.message.reply_photo(photo=photo, caption=caption)
                else:
                    await update.message.reply_photo(photo=photo, caption=caption)
        idx += 1
        doc_info['current_idx'] = idx
        if not send_all: break
    if idx < total:
        keyboard = [[
            InlineKeyboardButton("➡️ နောက်တစ်မျက်နှာ", callback_data="next_page"),
            InlineKeyboardButton("⏩ အကုန်ထုတ်မယ်", callback_data="extract_all")
        ]]
        text = f"စာမျက်နှာ {idx} ပို့ပြီးပါပြီ။ ကျန်ရှိသည်များကို ဆက်လက်ထုတ်ယူမလား?"
        if update.callback_query:
            await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        text = "✅ ဖိုင်တစ်ခုလုံး လုပ်ဆောင်ပြီးစီးပါပြီ။"
        if update.callback_query:
            await update.callback_query.message.reply_text(text)
        else:
            await update.message.reply_text(text)
        context.user_data['current_doc'] = None

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle buttons."""
    query = update.callback_query
    await query.answer()
    if query.data == "help": await help_command(update, context)
    elif query.data == "features": await features_command(update, context)
    elif query.data == "main_menu": await start_command(update, context)
    elif query.data == "next_page": await send_next_part(update, context, False)
    elif query.data == "extract_all": await send_next_part(update, context, True)

async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text."""
    if not update.message or not update.message.text: return
    try:
        converted = clean_myanmar_text(update.message.text)
        quoted = f"> {converted.replace(chr(10), chr(10) + '> ')}"
        await update.message.reply_text(quoted)
    except:
        await update.message.reply_text("❌ အမှားရှိနေပါသည်။")

def main() -> None:
    """Run Bot."""
    if not TOKEN: sys.exit(1)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_incoming_message))
    application.run_polling()

if __name__ == "__main__":
    main()
