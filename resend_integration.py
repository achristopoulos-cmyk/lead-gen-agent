"""
Resend Email Integration
Handles sending outreach emails via Resend API.
https://resend.com/docs/api-reference
"""

import requests
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EmailResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class ResendClient:
    """
    Client for Resend email API.
    Simple, reliable email sending for outreach sequences.
    """

    def __init__(self, api_key: str = None, from_email: str = None, from_name: str = None):
        self.api_key = api_key
        self.from_email = from_email or "hello@yourdomain.com"
        self.from_name = from_name or "Your Name"
        self.base_url = "https://api.resend.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}

    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str = None,
        text_body: str = None,
        reply_to: str = None,
        tags: List[Dict] = None
    ) -> EmailResult:
        """
        Send an email via Resend.

        Args:
            to: Recipient email address
            subject: Email subject line
            html_body: HTML content (optional)
            text_body: Plain text content (required if no html_body)
            reply_to: Reply-to address (optional)
            tags: List of tags for tracking (optional)

        Returns:
            EmailResult with success status and message_id or error
        """
        if not self.api_key:
            print("[RESEND] API key not configured - email not sent")
            return EmailResult(success=False, error="API key not configured")

        # Build email payload
        payload = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [to],
            "subject": subject
        }

        if html_body:
            payload["html"] = html_body
        if text_body:
            payload["text"] = text_body
        if reply_to:
            payload["reply_to"] = reply_to
        if tags:
            payload["tags"] = tags

        # Must have either html or text
        if not html_body and not text_body:
            return EmailResult(success=False, error="Email must have html or text body")

        try:
            response = requests.post(
                f"{self.base_url}/emails",
                headers=self.headers,
                json=payload
            )

            if response.status_code in [200, 201]:
                data = response.json()
                message_id = data.get("id")
                print(f"[RESEND] Email sent to {to} | ID: {message_id}")
                return EmailResult(success=True, message_id=message_id)
            else:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
                print(f"[RESEND] Error: {error_msg}")
                return EmailResult(success=False, error=error_msg)

        except Exception as e:
            print(f"[RESEND] Exception: {str(e)}")
            return EmailResult(success=False, error=str(e))

    def _sanitize_tag_value(self, value: str) -> str:
        """Sanitize tag values to only contain ASCII letters, numbers, underscores, or dashes."""
        import re
        # Replace any character that isn't alphanumeric, underscore, or dash with underscore
        return re.sub(r'[^a-zA-Z0-9_-]', '_', value)

    def send_outreach_email(
        self,
        to: str,
        subject: str,
        body: str,
        lead_id: str = None,
        sequence_step: str = None
    ) -> EmailResult:
        """
        Send an outreach email with tracking tags.

        Args:
            to: Recipient email
            subject: Email subject
            body: Plain text email body (will be converted to simple HTML)
            lead_id: Lead identifier for tracking
            sequence_step: Which step in the sequence (e.g., "initial_outreach")
        """
        # Convert plain text to simple HTML with proper formatting
        html_body = self._text_to_html(body)

        # Build tracking tags (sanitize values for Resend API compatibility)
        tags = []
        if lead_id:
            tags.append({"name": "lead_id", "value": self._sanitize_tag_value(lead_id)})
        if sequence_step:
            tags.append({"name": "sequence_step", "value": self._sanitize_tag_value(sequence_step)})
        tags.append({"name": "campaign", "value": "lead_gen_outreach"})

        return self.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=body,
            reply_to=self.from_email,
            tags=tags if tags else None
        )

    def _text_to_html(self, text: str) -> str:
        """Convert plain text email to simple HTML."""
        # Escape HTML characters
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")

        # Convert line breaks to HTML
        paragraphs = text.split("\n\n")
        html_paragraphs = []

        for p in paragraphs:
            # Convert single line breaks within paragraphs
            p = p.replace("\n", "<br>")
            if p.strip():
                html_paragraphs.append(f"<p style='margin: 0 0 16px 0; line-height: 1.6;'>{p}</p>")

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; padding: 20px;">
    {''.join(html_paragraphs)}
</body>
</html>
"""
        return html_body

    def get_email_status(self, email_id: str) -> dict:
        """Get the status of a sent email."""
        if not self.api_key:
            return {"error": "API key not configured"}

        try:
            response = requests.get(
                f"{self.base_url}/emails/{email_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}

        except Exception as e:
            return {"error": str(e)}

    def verify_connection(self) -> dict:
        """Verify the Resend API connection by checking domains."""
        if not self.api_key:
            return {"connected": False, "error": "API key not configured"}

        try:
            response = requests.get(
                f"{self.base_url}/domains",
                headers=self.headers
            )

            if response.status_code == 200:
                data = response.json()
                domains = data.get("data", [])
                return {
                    "connected": True,
                    "domains": [d.get("name") for d in domains],
                    "domain_count": len(domains)
                }
            else:
                return {"connected": False, "error": response.text}

        except Exception as e:
            return {"connected": False, "error": str(e)}


class EmailQueue:
    """
    Simple email queue for managing scheduled sends.
    Stores emails to be sent and tracks sent status.
    """

    def __init__(self):
        self.queue = []
        self.sent = []

    def add(self, to: str, subject: str, body: str, send_at: datetime = None,
            lead_id: str = None, sequence_step: str = None):
        """Add an email to the queue."""
        email = {
            "to": to,
            "subject": subject,
            "body": body,
            "send_at": send_at or datetime.now(),
            "lead_id": lead_id,
            "sequence_step": sequence_step,
            "status": "queued",
            "queued_at": datetime.now().isoformat()
        }
        self.queue.append(email)
        return email

    def get_pending(self) -> List[dict]:
        """Get emails that are ready to send."""
        now = datetime.now()
        return [e for e in self.queue if e["send_at"] <= now and e["status"] == "queued"]

    def mark_sent(self, email: dict, message_id: str):
        """Mark an email as sent."""
        email["status"] = "sent"
        email["message_id"] = message_id
        email["sent_at"] = datetime.now().isoformat()
        self.sent.append(email)
        self.queue.remove(email)

    def mark_failed(self, email: dict, error: str):
        """Mark an email as failed."""
        email["status"] = "failed"
        email["error"] = error
        email["failed_at"] = datetime.now().isoformat()


# Test the integration
if __name__ == "__main__":
    import json

    # Load config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except:
        config = {}

    api_key = config.get("resend_api_key")

    print("=" * 50)
    print("RESEND EMAIL INTEGRATION TEST")
    print("=" * 50)

    if not api_key:
        print("\nResend API key not configured.")
        print("Add 'resend_api_key' to config.json")
        print("\nGet your API key from: https://resend.com/api-keys")
    else:
        client = ResendClient(
            api_key=api_key,
            from_email=config.get("resend_from_email", "hello@yourdomain.com"),
            from_name=config.get("resend_from_name", "Your Name")
        )

        print("\nVerifying connection...")
        result = client.verify_connection()

        if result.get("connected"):
            print(f"Connected!")
            print(f"Verified domains: {result.get('domains', [])}")
        else:
            print(f"Connection failed: {result.get('error')}")
