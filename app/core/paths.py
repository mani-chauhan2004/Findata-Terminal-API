import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

# Static icon directories
STATIC_ICONS_ROOT     = PROJECT_ROOT / "static" / "icons"
STOCKS_ICONS_DIR      = STATIC_ICONS_ROOT / "stocks"
ALL_SYMBOLS_ICONS_DIR = STATIC_ICONS_ROOT / "all_symbols"
NEWS_ICONS_DIR        = STATIC_ICONS_ROOT / "news"
COUNTRIES_ICONS_DIR   = STATIC_ICONS_ROOT / "countries"
TOKENS_ICONS_DIR      = STATIC_ICONS_ROOT / "tokens"
