"""
Myanmar Font Universal Normalizer and Converter Module
Handles robust detection and conversion between Zawgyi and Pyidaungsu Unicode.
"""

import re
import rabbit
import logging
import unicodedata

logger = logging.getLogger(__name__)

def to_pyidaungsu(text: str) -> str:
    """
    Universally normalizes and converts incoming Myanmar text to clean Pyidaungsu Unicode.
    """
    if not text:
        return ""
    
    # Normalize Unicode composition first
    text = unicodedata.normalize('NFC', text)
    
    # Aggressively fix OCR visual order and Zawgyi encoding.
    # Rabbit zg2uni is safe to run on Unicode; it fixes visual ordering.
    if re.search(r'[\u1000-\u109F]', text):
        try:
            text = rabbit.zg2uni(text)
        except Exception as e:
            logger.error(f"Rabbit conversion failed: {e}")
            
    return unicodedata.normalize('NFC', text)
