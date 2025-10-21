# indiamart_send_reply_bot

A small Selenium-based bot that logs into the IndiaMART seller portal, searches buy-leads by keywords, and sends replies when lead criteria (quantity, state, keywords) match.

This README explains how to configure the bot using environment variables, how to provide keyword/quantity mappings, and how to run it on a Windows development machine.

## What this does
- Logs into https://seller.indiamart.com/ using a mobile number and password
- Searches buy-leads for a set of keywords
- Filters leads by quantity, state, and similarity to configured keyword synonyms
- Opens leads and attempts to click "Contact Buyer Now" → "Send Reply"

## Security and safety
- Do NOT commit your `.env` file. This repository provides `.env.example` and `.gitignore` excludes `.env`.
- Keep `NEW_KEY_DICT` small in the env; for large mappings use a separate JSON file (I can help convert to file-based loading).

## Requirements
- Python 3.8+
- Chrome browser and a matching ChromeDriver installed on your machine. Update `service = Service(...)` in `main.py` to point to your chromedriver binary.
- Packages in `requirements.txt` (install with pip)

## Install
Open PowerShell and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks script execution, run (as admin) once to allow activation scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- `NEW_KEY_DICT` must be a JSON object mapping keyword → array of similar phrases. The code validates types and enforces reasonable size limits.

## Running
Run from PowerShell in the project root:

```powershell
.\.venv\Scripts\Activate.ps1
# ensure your .env is present and configured
python main.py
```

The script will run in a loop (see `run_bot()` in `main.py`). Stop it with Ctrl+C.

## Troubleshooting
- Selenium/ChromeDriver version mismatch: ensure your ChromeDriver matches your Chrome browser version.
- If logins fail, check XPaths in `main.py` — websites may change structure and require XPath updates.
- If you see parsing errors for env variables, check JSON syntax and length.

## Next improvements (suggested)
- Move `NEW_KEY_DICT` to a separate `key_mapping.json` file for larger mappings.
- Add unit tests for env parsing and mapping validation.
- Add retries and better error handling for flaky network interactions.
