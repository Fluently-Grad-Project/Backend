import gettext
from pathlib import Path
from contextvars import ContextVar

translator_var = ContextVar("translator", default=lambda x: x)

def set_translator(lang: str):
    locales_dir = Path(__file__).parent / "translations"
    translator = gettext.translation("messages", localedir=locales_dir, languages=[lang], fallback=True)
    print(f"🌍 Language set to: {lang}")
    translator_var.set(translator.gettext)

def _(text: str) -> str:
    return translator_var.get()(text)
