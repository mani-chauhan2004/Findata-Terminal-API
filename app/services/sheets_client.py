import re
import json
import gspread
from google.oauth2.service_account import Credentials
from app.core.config import settings
from app.core.paths import STOCKS_ICONS_DIR, ALL_SYMBOLS_ICONS_DIR, COUNTRIES_ICONS_DIR, NEWS_ICONS_DIR

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

_client: gspread.Client | None = None


def _get_client() -> gspread.Client:
    global _client
    if _client is None:
        creds_info = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_info, scopes=_SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _static_icon_url(icons_dir, name: str, source_url: str) -> str:
    safe_name = re.sub(r"[^\w\-.]", "_", name).strip("_")
    last_segment = source_url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    raw_ext = last_segment.rsplit(".", 1)[-1] if "." in last_segment else ""
    suffix = raw_ext if raw_ext.isalpha() and len(raw_ext) <= 4 else "png"
    base = settings.BASE_API_URL.rstrip("/")
    return f"{base}/static/icons/{icons_dir.name}/{safe_name}.{suffix}"


class SheetsClient:
    def get_symbols(self) -> list[dict]:
        gc = _get_client()
        sh = gc.open_by_key(settings.SYMBOLS_SPREADSHEET_ID)
        ws = sh.get_worksheet(0)
        records = ws.get_all_records()
        return [
            {
                "ticker": row.get("Ticker", ""),
                "name": row.get("Company Name", ""),
                "logo_url": _static_icon_url(STOCKS_ICONS_DIR, row.get("Ticker", ""), row.get("Logo URL", "")),
                "twitter": row.get("Twitter", "") or None,
                "linkedin": row.get("LinkedIn", "") or None,
            }
            for row in records
            if row.get("Ticker")
        ]

    def get_news_portal_symbols(self) -> list[dict]:
        gc = _get_client()
        sh = gc.open_by_key(settings.SYMBOLS_SPREADSHEET_ID)
        ws = sh.get_worksheet(1)
        records = ws.get_all_records()
        return [
            {
                "news_portal": row.get("News_Portal", ""),
                "website_url": row.get("Website URL", ""),
                "logo_url": _static_icon_url(NEWS_ICONS_DIR, row.get("News_Portal", ""), row.get("Logo URL", "")),
            }
            for row in records
            if row.get("News_Portal")
        ]

    def get_country_flags(self) -> list[dict]:
        gc = _get_client()
        sh = gc.open_by_key(settings.SYMBOLS_SPREADSHEET_ID)
        ws = sh.get_worksheet(2)
        records = ws.get_all_records()
        return [
            {
                "country": row.get("Country", ""),
                "flag_url": _static_icon_url(COUNTRIES_ICONS_DIR, row.get("Country", ""), row.get("Logo URL", "")),
            }
            for row in records
            if row.get("Country")
        ]

    def get_all_symbols(self) -> list[dict]:
        gc = _get_client()
        sh = gc.open_by_key(settings.SYMBOLS_SPREADSHEET_ID)
        ws = sh.get_worksheet(3)
        records = ws.get_all_records()
        return [
            {
                "ticker": row.get("Ticker", ""),
                "logo_url": _static_icon_url(ALL_SYMBOLS_ICONS_DIR, row.get("Ticker", ""), row.get("Logo URL", "")),
                "name": row.get("Company Name", ""),
            }
            for row in records
            if row.get("Ticker")
        ]


sheets_client = SheetsClient()
