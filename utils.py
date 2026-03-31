import asyncio
import logging
import os
import zipfile
from datetime import datetime
from config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{LOG_DIR}/app.log"),
            logging.StreamHandler()
        ]
    )

async def retry_async(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay * (2 ** attempt))

def zip_screenshots(folder_path):
    zip_name = f"screenshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(folder_path, zip_name)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(folder_path):
            if file.endswith(".png"):
                zipf.write(os.path.join(folder_path, file), file)

    return zip_path
