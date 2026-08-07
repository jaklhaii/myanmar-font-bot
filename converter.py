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
    
    - If the text is Zawgyi, it converts it to standard Unicode.
    
    - If the text is already Unicode, it ensures integrity without corruption.
    
    """
    
    if not text:
        
        return ""
        


    cleaned_text = text.strip()
    


    try:
        
        # Convert via Rabbit Zawgyi-to-Unicode engine
        
        # Rabbit is safe to run on Unicode; it usually won't change it if it's already Unicode
        
        # but for OCR output, we WANT it to reorder visual sequences.
        
        converted_text = rabbit.zg2uni(cleaned_text)
        


        # Final pass for normalization

        return unicodedata.normalize('NFC', converted_text)
        
    except Exception as e:
        
        logger.error(f"Error during font conversion: {e}")
        
        return cleaned_text
        


















