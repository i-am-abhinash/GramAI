from backend.locale.strings_en import STRINGS_EN
from backend.locale.strings_te import STRINGS_TE

class I18n:
    _current_lang = "te" # default to Telugu
    
    @classmethod
    def set_language(cls, lang_code):
        if lang_code in ['en', 'te']:
            cls._current_lang = lang_code
            
    @classmethod
    def get(cls, key):
        if cls._current_lang == "te":
            return STRINGS_TE.get(key, STRINGS_EN.get(key, key))
        return STRINGS_EN.get(key, key)
