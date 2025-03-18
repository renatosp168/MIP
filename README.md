# Website/IP Monitor

This Python script monitors the status of a list of websites or IP addresses. It sends an email notification when the status of any website/IP changes (from online to offline or vice versa). The script dynamically loads the list of targets from a `targets.txt` file and reads configurations from a `config.ini` file.

---

## Features
- **Dynamic Target Loading**: Add or remove websites/IPs from `targets.txt` without restarting the script.
- **Email Notifications**: Receive email alerts when the status of a website/IP changes.
- **Initial Status Report**: Sends an email with the initial status of all websites/IPs when the script starts.
- **Error Handling**: Handles connection errors, timeouts, and other exceptions to accurately detect website/IP status.
- **Configurable**: All settings (email, monitoring interval, etc.) are configurable via `config.ini`.

---

## Prerequisites
- Python 3.x
- Required Python packages: `requests`, `configparser`

Install the required packages using:
```bash
pip install requests