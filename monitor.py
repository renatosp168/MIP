import requests
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import io

# Function to remove comments from config file
def remove_comments(config_content):
    lines = config_content.splitlines()
    cleaned_lines = [line for line in lines if not line.strip().startswith('#')]
    return '\n'.join(cleaned_lines)

# Load configurations
config = configparser.ConfigParser()
with open('config.ini', 'r') as config_file:
    config_content = config_file.read()
    cleaned_config = remove_comments(config_content)
    config.read_string(cleaned_config)

# Email settings
SMTP_SERVER = config['email']['smtp_server']
SMTP_PORT = int(config['email']['smtp_port'])
SENDER_EMAIL = config['email']['sender_email']
SENDER_PASSWORD = config['email']['sender_password']
RECEIVER_EMAIL = config['email']['receiver_email']

# Monitor settings
CHECK_INTERVAL = int(config['monitor']['check_interval'])

# Track status of targets
status_dict = {}  # Stores the current status of each target

def check_status(target):
    try:
        response = requests.get(target if target.startswith(('http://', 'https://')) else f'http://{target}', timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False
    except requests.Timeout:
        return False
    except requests.ConnectionError:
        return False

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def load_targets():
    with open('targets.txt', 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip() and not line.strip().startswith('#')]


def monitor_targets():
    global status_dict
    targets = load_targets()

    # Initialize new targets
    for target in targets:
        if target not in status_dict:
            status_dict[target] = None  # Initialize status for new target

    # Check status of all targets
    status_changes = []
    for target in targets:
        current_status = check_status(target)

        firstStatus = status_dict[target] is None 

        # Detect status change
        if status_dict[target] is None or current_status != status_dict[target]:
            status_changes.append({
                "target": target,
                "status": "online" if current_status else "offline",
                "previous_status": "online" if status_dict[target] else "offline"
            })

        # Update the status in the dictionary
        status_dict[target] = current_status

    # Send email only if there are status changes
    if status_changes:
        email_body = "Website/IP Status Changes:\n\n"
        for change in status_changes:
            if(firstStatus):
                email_body += f"- {change['target']}: {change['status']} \n"
            else:
                email_body += f"- {change['target']}: Changed from {change['previous_status']} to {change['status']}\n"

        send_email("Website/IP Status Change Alert", email_body)
    else:
        # Print a message if there are no changes
        print("No status changes detected in this iteration.")

if __name__ == "__main__":
    print("Starting monitor...")
    # Start monitoring
    while True:
        monitor_targets()
        time.sleep(60*CHECK_INTERVAL)