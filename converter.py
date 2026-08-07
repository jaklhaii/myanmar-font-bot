"""
Myanmar Font Universal Normalizer and Converter Module
Handles robust detection and conversion between Zawgyi and Pyidaungsu Unicode.
"""

import re
import rabbit
import logging
import unicodedata

logger = logging.getLogger(__name__)

def is_zawgyi(text: str) -> bool:
    """Robust heuristic to detect if text is Zawgyi encoded."""
    if not text:
        return False
    zg_chars = r'[\u107e-\u1084\u1088\u1089\u1090\u1091\u1092\u1097\u1033\u1034\u1035\u1039]'
    if re.search(zg_chars, text):
        return True
    if re.search(r'[\u1031\u103c][\u1000-\u1021]', text):
        return True
    return False

def to_pyidaungsu(text: str) -> str:
    """
    Universally normalizes and converts incoming Myanmar text to clean Pyidaungsu Unicode.
    """
    if not text:
        return ""
    
    text = unicodedata.normalize('NFC', text)
    
    if is_zawgyi(text) or '\u1031' in text:
        try:
            text = rabbit.zg2uni(text)
        except Exception as e:
            logger.error(f"Rabbit conversion failed: {e}")
            
    return unicodedata.normalize('NFC', text)
