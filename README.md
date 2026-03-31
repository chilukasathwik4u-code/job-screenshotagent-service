# Job Screenshot Agent

A production-ready Python tool that **reads job listing URLs from an Excel file**, captures **full-page screenshots** using Playwright, and **emails the results** as a ZIP attachment — all asynchronously.

---

## Features

| Feature | Description |
|---|---|
| **Async Playwright** | Fast, parallel screenshot capture using headless Chromium |
| **Retry with Backoff** | Auto-retries failed URLs up to 3 times with exponential backoff (2s → 4s → 8s) |
| **Error Classification** | Categorizes failures (DNS, Timeout, SSL, 404, 403, 500, etc.) |
| **Error Screenshots** | Captures screenshots of error pages (404, 500) for debugging |
| **Structured Logging** | Logs to both console and `logs/app.log` |
| **ZIP Delivery** | Packages all screenshots into a timestamped ZIP file |
| **Email Report** | Sends a summary email with the ZIP attached via Gmail SMTP |
| **Concurrency Control** | Limits parallel tasks (default: 3) to avoid overloading |

---

## Project Structure

```
job-screenshot-agent/
├── main.py                  # Entry point — orchestrates the pipeline
├── config.py                # Environment-based configuration
├── screenshot_service.py    # Async screenshot capture with error handling
├── email_service.py         # SMTP email with ZIP attachment
├── utils.py                 # Logger setup, retry logic, ZIP utility
├── requirements.txt         # Python dependencies
├── .env                     # Email credentials (not committed)
├── screenshots/             # Output — captured screenshots
└── logs/                    # Output — application logs
```

---

## Quick Start

### 1. Clone & Install

```bash
cd job-screenshot-agent
pip install -r requirements.txt
playwright install
```

### 2. Configure Email

Edit `.env` with your Gmail credentials:

```env
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_RECEIVER=receiver@gmail.com
```

> **Important:** You must use a [Gmail App Password](https://myaccount.google.com/apppasswords), **not** your regular password. Enable [2-Step Verification](https://myaccount.google.com/security) first.

### 3. Add Your Excel File

Place an Excel file named `option1_job_links.xlsx` in the project root. It must have a column named **`URL`**:

| URL |
|---|
| https://www.anthropic.com/jobs |
| https://boards.greenhouse.io/figma/jobs/5227937004 |
| https://www.linkedin.com/jobs/view/3847201938 |

### 4. Run

```bash
python3 main.py
```

---

## Sample Output

```
2026-03-31 19:44:52 - INFO - Reading Excel file...
2026-03-31 19:44:52 - INFO - Processing 5 URLs...
2026-03-31 19:44:57 - INFO - SUCCESS [3]: https://boards.greenhouse.io/figma/jobs/5227937004
2026-03-31 19:45:03 - ERROR - FAILED [4]: https://careers.techcorp-xyz99999.com/... | DNS_ERROR: Domain does not exist
2026-03-31 19:45:06 - ERROR - FAILED [2]: https://www.amazon.jobs/... | NOT_FOUND: Page not found (404) (screenshot saved)
2026-03-31 19:45:06 - INFO - SUCCESS [5]: https://www.linkedin.com/jobs/view/3847201938
2026-03-31 19:45:14 - INFO - SUCCESS [1]: https://www.anthropic.com/jobs
2026-03-31 19:45:14 - INFO - Zipping screenshots...
2026-03-31 19:45:51 - INFO - Email sent successfully
2026-03-31 19:45:51 - INFO - Process completed!
```

---

## Error Handling

The agent classifies URL failures into specific categories:

| Error Code | Cause |
|---|---|
| `DNS_ERROR` | Domain doesn't exist or can't be resolved |
| `CONNECTION_REFUSED` | Server refused the connection |
| `TIMEOUT` | Page took too long to load |
| `SSL_ERROR` | SSL/TLS certificate issue |
| `REDIRECT_ERROR` | Too many redirects |
| `NOT_FOUND` | HTTP 404 — page not found |
| `FORBIDDEN` | HTTP 403 — access denied |
| `SERVER_ERROR` | HTTP 500 — internal server error |

- **HTTP errors (404, 403, 500):** Screenshot is captured *before* marking as failed
- **Network errors (DNS, timeout):** A blank error screenshot is saved when possible
- **All failures:** Retried 3 times with exponential backoff before giving up

---

## Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP server address |
| `SMTP_PORT` | `587` | SMTP port (TLS) |
| `SCREENSHOT_DIR` | `screenshots` | Output folder for screenshots |
| `LOG_DIR` | `logs` | Output folder for log files |
| `MAX_RETRIES` | `3` | Number of retry attempts per URL |
| `TIMEOUT` | `30000` | Page load timeout in milliseconds |
| `CONCURRENT_TASKS` | `3` | Max parallel screenshot tasks |

---

## Email Report

The email includes:
- **Subject:** `Job Screenshot Report`
- **Body:** Summary with ✅ successes and ❌ failures (with error type & details)
- **Attachment:** Timestamped ZIP file containing all screenshots (including error pages)

---

## Dependencies

- **pandas** + **openpyxl** — Excel file reading
- **playwright** — Headless browser for screenshots
- **python-dotenv** — Environment variable management

---

## License

MIT
