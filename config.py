import os
from datetime import timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

# 檔案與資料夾
DB_PATH = BASE_DIR / "db" / "cyut_park.db"
RICH_MENU_FLEX_MESSAGES_PATH = (
    BASE_DIR / "Line_template" / "rich_menu_flex_message.json"
)
MCP_TOOL_FLEX_LINE_MESSAGES_PATH = (
    BASE_DIR / "Line_template" / "mcp_tool_line_flex_message.json"
)

# API 金鑰與 LINE 帳號
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEATHER_API_KEY = os.getenv("Weather_API_KEY")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
WORKER_LINE_USER_ID = os.getenv("WORKER_LINE_USER_ID")
WORKER_CHANNEL_ACCESS_TOKEN = os.getenv("WORKER_CHANNEL_ACCESS_TOKEN")

# LINE Messaging API
LINE_API_BASE = "https://api.line.me/v2/bot"

# Flask 與樂園資料
ANNOUNCEMENT_PUBLISHER = "朝陽樂園管理單位"
TAIPEI_TIMEZONE = timezone(timedelta(hours=8))
