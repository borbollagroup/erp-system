import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def gas(to, subject, body, html_body=None, cc=None, bcc=None):
    """
    Send an email via your Google Apps Script relay.
    Raises on failure.
    
    Arguments:
      to        -- recipient email (string or list)
      subject   -- message subject
      body      -- plain-text body
      html_body -- optional HTML body
      cc        -- optional CC email (string or list)
      bcc       -- optional BCC email (string or list)
    """
    url = "https://script.google.com/macros/s/AKfycbzLld3F1HluyX-2XjYH8e1QoB7c7-kIID11YmQLanjGYWSHXDnuHtD9CKkeGRWy52sx2A/exec"  # or settings.GAS_RELAY_URL

    payload = {
        "to":      to,
        "subject": subject,
        "body":    body,
    }
    if html_body is not None:
        payload["htmlBody"] = html_body
    if cc:
        payload["cc"] = cc
    if bcc:
        payload["bcc"] = bcc

    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "OK":
            raise RuntimeError(f"GAS relay error: {data.get('message')}")
        return data
    except Exception:
        logger.exception("Failed to send email via GAS relay")
        raise
