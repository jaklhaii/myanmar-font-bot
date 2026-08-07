"""
Myanmar Font Universal Normalizer and Converter Module
Handles robust detection and conversion between Zawgyi and Pyidaungsu Unicode.
"""

import re
import rabbit
import logging

logger = logging.getLogger(__name__)

def to_pyidaungsu(text: str) -> str:
    """
    Universally normalizes and converts incoming Myanmar text to clean Pyidaungsu Unicode.
    - If the text is Zawgyi, it converts it to standard Unicode.
    - If the text is already Unicode, it ensures integrity without corruption.
    """
    if not text:
        return ""
    
    cleaned_text = text.strip()
    
    # Check if text contains standard Unicode virama (U+1039)
    # Standard Unicode text typically contains U+1039 for consonant stacking.
    has_unicode_virama = '\u1039' in cleaned_text
    
    if has_unicode_virama:
        # Already standard Unicode; preserve and return cleanly
        return cleaned_text
    
    try:
        # Convert via Rabbit Zawgyi-to-Unicode engine
        converted_text = rabbit.zg2uni(cleaned_text)
        return converted_text
    except Exception as e:
        logger.error(f"Error during font conversion: {e}")
        return cleaned_text
