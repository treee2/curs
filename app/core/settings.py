import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_admin_id: str | None = os.getenv("TELEGRAM_ADMIN_ID")

    webapp_host: str = os.getenv("WEBAPP_HOST", "0.0.0.0")
    webapp_port: int = int(os.getenv("WEBAPP_PORT", "8000"))
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")

    yookassa_shop_id: str = os.getenv("YOOKASSA_SHOP_ID", "")
    yookassa_secret_key: str = os.getenv("YOOKASSA_SECRET_KEY", "")
    yookassa_receipt_email: str | None = os.getenv("YOOKASSA_RECEIPT_EMAIL")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:////workspace/app.db")
    files_dir: str = os.getenv("FILES_DIR", "/workspace/files")

settings = Settings()
