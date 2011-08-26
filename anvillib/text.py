import unicodedata
import re

def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s)
                    if unicodedata.category(c) != 'Mn'))

def normalize_name(raw_name):
    return re.sub('[^0-9a-zA-Z_-]', '', strip_accents(raw_name).replace(' ', '-'))
