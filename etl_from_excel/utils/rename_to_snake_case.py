import unicodedata
import re

def rename_to_snake_case(text):
    """
    Function to convert a text to snake_case
    """
    text = unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')
    
    text = text.replace('$', 's')
    
    text = re.sub(r'[^\w\s]', '_', text)
    
    text = text.replace(' ', '_')
    
    text = re.sub(r'__+', '_', text)
    
    if text.endswith('_'):
        text = text[:-1]
    
    return text