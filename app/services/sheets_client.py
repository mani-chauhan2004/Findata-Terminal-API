import json
import gspread
from google.oauth2.service_account import Credentials
from app.core.config import settings

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

_client: gspread.Client | None = None


def _get_client() -> gspread.Client:
    global _client
    if _client is None:
        creds_info = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_info, scopes=_SCOPES)
        _client = gspread.authorize(creds)
    return _client


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
                "logo_url": row.get("Logo URL", ""),
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
                "news_portal": row.get("News Portal", ""),
                "website_url": row.get("Website URL", ""),
                "logo_url": row.get("Logo URL", ""),
            }
            for row in records
            if(row.get("News Portal"))
        ]


sheets_client = SheetsClient()
