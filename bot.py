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
    # Common Zawgyi characters and PUA range
    zg_chars = r'[\u107e-\u1084\u1088\u1089\u1090\u1091\u1092\u1097\u1033\u1034\u1035\u1039]'
    if re.search(zg_chars, text):
        return True
    # E-kar (U+1031) or Medial Ra (U+103C) before a consonant (Visual order)
    if re.search(r'[\u1031\u103c][\u1000-\u1021]', text):
        return True
    # Consonant + Medial Ra + Medial Wa (Common visual pattern in OCR)
    if re.search(r'[\u1000-\u1021][\u103C][\u103D]', text):
        return True
    return False

def clean_myanmar_text(text: str) -> str:
    """Clean and convert Myanmar text with smart detection."""
    if not text:
        return ""
    
    # Step 1: PUA cleaning (Common in some PDF fonts)
    pua_map = {
        '\uE107': '\u1014', #  -> န
        '\uE100': '\u1000',
        '\uE101': '\u1001',
    }
    for k, v in pua_map.items():
        text = text.replace(k, v)
    text = re.sub(r'[\uE000-\uF8FF]', '', text)
    
    # Step 2: Aggressive Font Conversion
    # OCR output is often mixed or visual-order Unicode. 
    # converter.to_pyidaungsu now handles this by always attempting conversion.
    try:
        text = converter.to_pyidaungsu(text)
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        
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
        images = convert_from_path(input_path, first_page=page_idx+1, last_page=page_idx+1, dpi=300)
        if not images:
            return f"Error: Could not render page {page_idx+1}"
        text = pytesseract.image_to_string(images[0], lang='mya')
        return clean_myanmar_text(text)
    except Exception as e:
        logger.error(f"OCR Error on page {page_idx}: {e}")
        return f"(OCR အမှား: {e})"

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process uploaded documents."""
    doc = update.message.document
    file_ext = os.path.splitext(doc.file_name)[1].lower()
    
    status_msg = await update.message.reply_text("⏳ ဖိုင်ကို စစ်ဆေးနေပါသည်...")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, doc.file_name)
        new_file = await context.bot.get_file(doc.file_id)
        await new_file.download_to_drive(file_path)
        
        if file_ext == '.pdf':
            try:
                reader = PdfReader(file_path)
                total_pages = len(reader.pages)
                await status_msg.edit_text(f"📄 PDF စာမျက်နှာ {total_pages} ခု တွေ့ရှိသည်။ OCR စတင်နေပါသည်...")
                
                # Extract first page as preview
                first_page_text = extract_pdf_page_ocr(file_path, 0)
                response = f"--- Page 1 (OCR) ---\n\n{first_page_text}"
                
                keyboard = []
                if total_pages > 1:
                    keyboard.append([InlineKeyboardButton("➡️ နောက်တစ်မျက်နှာ", callback_data=f"pdf_1_{doc.file_id}")])
                
                await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit_text(f"❌ PDF ဖတ်ရာတွင် အမှားရှိပါသည်: {e}")
                
        elif file_ext == '.pptx':
            try:
                prs = Presentation(file_path)
                total_slides = len(prs.slides)
                await status_msg.edit_text(f"📊 PowerPoint Slide {total_slides} ခု တွေ့ရှိသည်။ Render လုပ်နေပါသည်...")
                
                img_path = render_pptx_slide(file_path, 0, total_slides)
                keyboard = []
                if total_slides > 1:
                    keyboard.append([InlineKeyboardButton("➡️ Next Slide", callback_data=f"pptx_1_{doc.file_id}")])
                
                await update.message.reply_photo(photo=open(img_path, 'rb'), reply_markup=InlineKeyboardMarkup(keyboard))
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit_text(f"❌ PPTX ဖတ်ရာတွင် အမှားရှိပါသည်: {e}")
        else:
            await status_msg.edit_text("❌ PDF သို့မဟုတ် PPTX ဖိုင်များကိုသာ လက်ခံပါသည်။")

async def send_next_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pagination for large texts or documents."""
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    file_type = data[0]
    next_idx = int(data[1])
    file_id = data[2]
    
    new_file = await context.bot.get_file(file_id)
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, "temp_file")
        await new_file.download_to_drive(file_path)
        
        if file_type == 'pdf':
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            text = extract_pdf_page_ocr(file_path, next_idx)
            response = f"--- Page {next_idx + 1} (OCR) ---\n\n{text}"
            
            keyboard = []
            row = []
            if next_idx > 0:
                row.append(InlineKeyboardButton("⬅️ ရှေ့တစ်မျက်နှာ", callback_data=f"pdf_{next_idx-1}_{file_id}"))
            if next_idx < total_pages - 1:
                row.append(InlineKeyboardButton("➡️ နောက်တစ်မျက်နှာ", callback_data=f"pdf_{next_idx+1}_{file_id}"))
            if row: keyboard.append(row)
            
            await query.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
            
        elif file_type == 'pptx':
            prs = Presentation(file_path)
            total_slides = len(prs.slides)
            img_path = render_pptx_slide(file_path, next_idx, total_slides)
            
            keyboard = []
            row = []
            if next_idx > 0:
                row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"pptx_{next_idx-1}_{file_id}"))
            if next_idx < total_slides - 1:
                row.append(InlineKeyboardButton("➡️ Next", callback_data=f"pptx_{next_idx+1}_{file_id}"))
            if row: keyboard.append(row)
            
            await query.message.reply_photo(photo=open(img_path, 'rb'), reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback queries."""
    query = update.callback_query
    data = query.data
    
    if data == "main_menu":
        await start_command(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data == "features":
        await features_command(update, context)
    elif data.startswith(('pdf_', 'pptx_')):
        await send_next_part(update, context)

async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plain text messages."""
    text = update.message.text
    if not text: return
    
    cleaned = clean_myanmar_text(text)
    await update.message.reply_text(cleaned)

def main():
    """Start the bot."""
    if not TOKEN:
        logger.error("No TOKEN found. Exiting.")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback_handler))
    
    logger.info("Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()
