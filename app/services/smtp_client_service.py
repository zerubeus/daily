import httpx

from app.core.logging import logger

SMTP_API_URL = "http://smtp:8025/api/send_email"


def send_email(to_email: str, code: str):
    try:
        response = httpx.post(SMTP_API_URL, json={"to": to_email, "code": code})
        response.raise_for_status()
        logger.info(f"Email sent to {to_email} with activation code {code}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise
