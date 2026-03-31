import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SCREENSHOT_DIR = "screenshots"
LOG_DIR = "logs"
MAX_RETRIES = 3
TIMEOUT = 30000
CONCURRENT_TASKS = 3
