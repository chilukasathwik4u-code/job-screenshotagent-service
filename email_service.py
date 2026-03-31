import smtplib
from email.message import EmailMessage
import logging
import os
from config import *

def send_email(results, zip_file):
    msg = EmailMessage()
    msg["Subject"] = "Job Screenshot Report"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    success_count = sum(1 for r in results if r["status"] == "success")
    fail_count = len(results) - success_count

    body = f"Execution Summary: {success_count} succeeded, {fail_count} failed\n"
    body += "=" * 50 + "\n\n"

    for r in results:
        if r["status"] == "success":
            body += f"✅ SUCCESS: {r['url']}\n"
        else:
            has_screenshot = "Yes" if r.get("file") else "No"
            body += f"❌ FAILED: {r['url']}\n"
            body += f"   Error Type: {r.get('error_code', 'UNKNOWN')}\n"
            body += f"   Details: {r.get('error_description', r['error'])}\n"
            body += f"   Screenshot Captured: {has_screenshot}\n\n"

    msg.set_content(body)

    # Attach ZIP
    with open(zip_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename=os.path.basename(zip_file)
        )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logging.info("Email sent successfully")

    except Exception as e:
        logging.error(f"Email failed: {e}")
