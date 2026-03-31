import os
import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from config import SCREENSHOT_DIR, TIMEOUT, CONCURRENT_TASKS
from utils import retry_async

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


ERROR_PATTERNS = {
    "err_name_not_resolved":    ("DNS_ERROR",           "Domain does not exist or cannot be resolved"),
    "err_connection_refused":   ("CONNECTION_REFUSED",  "Server refused the connection"),
    "err_connection_timed_out": ("TIMEOUT",             "Page took too long to load"),
    "timeout":                  ("TIMEOUT",             "Page took too long to load"),
    "err_ssl":                  ("SSL_ERROR",           "SSL/TLS certificate issue"),
    "ssl":                      ("SSL_ERROR",           "SSL/TLS certificate issue"),
    "err_cert":                 ("SSL_ERROR",           "SSL certificate error"),
    "err_too_many_redirects":   ("REDIRECT_ERROR",      "Too many redirects"),
    "err_connection_reset":     ("CONNECTION_RESET",    "Connection was reset by the server"),
    "err_connection_closed":    ("CONNECTION_CLOSED",   "Connection was closed unexpectedly"),
    "err_aborted":              ("ABORTED",             "Navigation was aborted"),
    "err_failed":               ("NETWORK_ERROR",       "Network request failed"),
    "enotfound":                ("DNS_ERROR",           "Domain not found"),
    "econnrefused":             ("CONNECTION_REFUSED",  "Connection refused"),
    "404":                      ("NOT_FOUND",           "Page not found (404)"),
    "not found":                ("NOT_FOUND",           "Page not found (404)"),
    "403":                      ("FORBIDDEN",           "Access denied (403)"),
    "forbidden":                ("FORBIDDEN",           "Access denied (403)"),
    "401":                      ("UNAUTHORIZED",        "Authentication required (401)"),
    "500":                      ("SERVER_ERROR",        "Internal server error (500)"),
    "502":                      ("BAD_GATEWAY",         "Bad gateway (502)"),
    "503":                      ("SERVICE_UNAVAILABLE", "Service unavailable (503)"),
    "internal server error":    ("SERVER_ERROR",        "Internal server error (500)"),
}


def classify_error(error_msg):
    """Classify the error into a human-readable category."""
    raw = str(error_msg)
    msg = raw.lower()
    code, description = next(
        (result for pattern, result in ERROR_PATTERNS.items() if pattern in msg),
        ("UNKNOWN_ERROR", raw)  # Use the raw error as the description if unknown
    )
    return code, description


async def capture_single(browser, url, index):
    async def task():
        page = await browser.new_page()
        try:
            response = await page.goto(url, timeout=TIMEOUT, wait_until="domcontentloaded")

            # Capture screenshot for ALL pages (success or error)
            file_path = f"{SCREENSHOT_DIR}/job_{index}.png"
            await page.screenshot(path=file_path, full_page=True)

            # Check HTTP status code AFTER taking screenshot
            if response and response.status >= 400:
                error_code, error_description = classify_error(f"HTTP {response.status}")
                logging.error(f"FAILED [{index}]: {url} | {error_code}: {error_description} (screenshot saved)")
                return {
                    "url": url,
                    "index": index,
                    "status": "failed",
                    "file": file_path,
                    "error": f"HTTP {response.status} - {response.status_text}",
                    "error_code": error_code,
                    "error_description": error_description
                }

            logging.info(f"SUCCESS [{index}]: {url}")
            return {
                "url": url,
                "index": index,
                "status": "success",
                "file": file_path,
                "http_status": response.status if response else None
            }
        finally:
            await page.close()

    try:
        return await retry_async(task)
    except Exception as e:
        # For network-level errors (DNS, connection refused), try to capture a blank/error page
        error_code, error_description = classify_error(e)
        error_file = None

        try:
            page = await browser.new_page()
            error_file = f"{SCREENSHOT_DIR}/job_{index}_error.png"
            await page.screenshot(path=error_file)
            await page.close()
            logging.error(f"FAILED [{index}]: {url} | {error_code}: {error_description} | Raw: {e} (error screenshot saved)")
        except Exception:
            logging.error(f"FAILED [{index}]: {url} | {error_code}: {error_description} | Raw: {e} (no screenshot possible)")

        return {
            "url": url,
            "index": index,
            "status": "failed",
            "file": error_file,
            "error": str(e),
            "error_code": error_code,
            "error_description": error_description
        }


async def capture_all(urls):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        semaphore = asyncio.Semaphore(CONCURRENT_TASKS)

        async def sem_task(url, i):
            async with semaphore:
                return await capture_single(browser, url, i)

        tasks = [sem_task(url, i + 1) for i, url in enumerate(urls)]
        results = await asyncio.gather(*tasks)

        await browser.close()

    return list(results)
