import pandas as pd
import asyncio
import logging
import os
from screenshot_service import capture_all
from email_service import send_email
from utils import setup_logger, zip_screenshots

def read_urls(file_path):
    df = pd.read_excel(file_path)

    if "URL" not in df.columns:
        raise ValueError("Missing 'URL' column in Excel")

    return df["URL"].dropna().tolist()

async def run():
    setup_logger()

    file_path = "/home/chilukasaisathwik/Downloads/option1_job_links.xlsx"

    logging.info("Reading Excel file...")
    urls = read_urls(file_path)

    logging.info(f"Processing {len(urls)} URLs...")

    results = await capture_all(urls)

    logging.info("Zipping screenshots...")
    zip_file = zip_screenshots("screenshots")

    logging.info("Sending email...")
    send_email(results, zip_file)

    logging.info("Process completed!")

if __name__ == "__main__":
    asyncio.run(run())

    
