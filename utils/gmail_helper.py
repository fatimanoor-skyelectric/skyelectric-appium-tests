import os
import re
import time
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

BASE_DIR         = os.path.dirname(os.path.dirname(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE       = os.path.join(BASE_DIR, 'token.json')


# -------------------------
# Gmail Auth
# -------------------------
def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# -------------------------
# MAIN OTP FETCHER
# -------------------------
def get_otp_from_gmail(
    sender_filter='skyelectric',
    subject_filter='OTP',
    wait_seconds=90,
    poll_interval=5,
    since_timestamp=None
):
    service = get_gmail_service()
    start_time = time.time()

    print(f"\n⏳ Waiting for OTP email (max {wait_seconds}s)...")

    while time.time() - start_time < wait_seconds:
        try:
            # ✅ Strong query (NO is:unread, NO marking emails)
            query = (
                f'from:{sender_filter} '
                f'subject:{subject_filter} '
                f'newer_than:5m'
            )

            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=5
            ).execute()

            messages = results.get('messages', [])
            print(f"   Found {len(messages)} candidate email(s)")

            if not messages:
                time.sleep(poll_interval)
                continue

            # ✅ Always take latest email first
            msg_stub = messages[0]

            msg = service.users().messages().get(
                userId='me',
                id=msg_stub['id'],
                format='full'
            ).execute()

            # -------------------------
            # Timestamp filtering
            # -------------------------
            msg_time = int(msg['internalDate']) / 1000

            if since_timestamp and msg_time < since_timestamp:
                print("   ⏩ Skipping old email (timestamp)")
                time.sleep(poll_interval)
                continue

            # -------------------------
            # Subject validation
            # -------------------------
            headers = msg.get('payload', {}).get('headers', [])
            subject = ""

            for h in headers:
                if h['name'].lower() == 'subject':
                    subject = h['value']
                    break

            if subject_filter.lower() not in subject.lower():
                print(f"   ⏩ Subject mismatch: {subject}")
                time.sleep(poll_interval)
                continue

            # -------------------------
            # Extract body
            # -------------------------
            body = extract_email_body(msg)
            print(f"   📧 Email body size: {len(body)} chars")

            otp = extract_otp_from_text(body)

            if otp:
                print(f"✅ OTP FOUND: {otp}")
                return otp
            else:
                print(f"   ❌ No OTP found. Preview: {body[:200]}")

        except Exception as e:
            print(f"⚠️ Gmail error: {e}")

        remaining = int(wait_seconds - (time.time() - start_time))
        print(f"   Retrying in {poll_interval}s ({remaining}s left)")
        time.sleep(poll_interval)

    print("❌ OTP not received within timeout")
    return None


# -------------------------
# EMAIL BODY EXTRACTION
# -------------------------
def extract_email_body(msg):
    payload = msg.get('payload', {})

    data = payload.get('body', {}).get('data', '')
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    for part in payload.get('parts', []):
        if part.get('mimeType') == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        for sub in part.get('parts', []):
            if sub.get('mimeType') == 'text/plain':
                data = sub.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    return ""


# -------------------------
# OTP EXTRACTION (FIXED)
# -------------------------
def extract_otp_from_text(text):
    """
    Safe OTP extraction (prevents random number capture)
    Supports 6–7 digit OTPs (your case: 5303341)
    """

    patterns = [
        r"'(\d{6,7})'",
        r'"(\d{6,7})"',
        r'OTP[:\s]+(\d{6,7})',
        r'Passcode[:\s]+(\d{6,7})',
        r'code[:\s]+(\d{6,7})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None