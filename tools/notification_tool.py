"""
tools/notification_tool.py
---------------------------
Async email notification tool for RTI workflow events.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)


async def _send_email_task(to_email: str, subject: str, body: str):
    """Send an email using async SMTP."""
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        logger.warning("[Notification] Email not configured. Skipping send.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_USER,
            password=settings.EMAIL_PASSWORD,
            start_tls=True,
        )
        logger.info(f"[Notification] Email sent to {to_email} | Subject: {subject}")
    except Exception as e:
        logger.error(f"[Notification] Email send failed: {e}")

import asyncio
_email_tasks = set()

async def _send_email(to_email: str, subject: str, body: str):
    task = asyncio.create_task(_send_email_task(to_email, subject, body))
    _email_tasks.add(task)
    task.add_done_callback(_email_tasks.discard)


async def send_approval_notification(
    request_id: str,
    formal_query: str,
    department: str,
    confidence: str,
    review_score: float,
    email: str,
):
    """Notify admin/user that RTI draft is ready for approval."""
    subject = f"[RTI-Agent] Review Required: {request_id}"
    body = (
        f"An RTI application is ready for your review.\n\n"
        f"Request ID: {request_id}\n"
        f"Department: {department} (confidence: {confidence})\n"
        f"Review Score: {review_score:.2f}/1.0\n\n"
        f"Draft:\n{formal_query[:500]}\n\n"
        f"To approve: POST /api/v1/approve/{request_id}\n"
        f"  Body: {{\"decision\": \"approved\", \"approved_by\": \"your-name\"}}\n\n"
        f"To reject: {{\"decision\": \"rejected\"}}"
    )
    if email:
        await _send_email(email, subject, body)
    # Always notify admin
    if settings.ADMIN_EMAIL and settings.ADMIN_EMAIL != email:
        await _send_email(settings.ADMIN_EMAIL, subject, body)


async def send_submission_notification(
    email: str,
    tracking_id: str,
    department: str,
    formal_query: str,
):
    """Notify citizen that RTI has been submitted."""
    subject = f"[RTI-Agent] Your RTI has been submitted — {tracking_id}"
    body = (
        f"Your RTI application has been successfully submitted.\n\n"
        f"Tracking ID: {tracking_id}\n"
        f"Department: {department}\n\n"
        f"Application:\n{formal_query[:300]}...\n\n"
        f"You can track your RTI status using your tracking ID.\n"
        f"Response expected within 30 days as per RTI Act 2005."
    )
    if email:
        await _send_email(email, subject, body)


async def send_public_info_notification(
    email: str,
    tracking_id: str,
    query: str,
    info: str,
):
    """Notify citizen that the requested information is already public."""
    subject = f"[RTI-Agent] Information Available Publicly — {tracking_id}"
    body = (
        f"Hello,\n\n"
        f"Thank you for using the RTI-Agent system.\n\n"
        f"The information you requested in your query is already publicly available!\n\n"
        f"**Query**:\n{query}\n\n"
        f"**Information/Link**:\n{info}\n\n"
        f"No formal RTI submission was necessary. You can refer to this email for future reference.\n"
        f"Tracking ID for reference: {tracking_id}\n\n"
        f"Have a great day!"
    )
    if email:
        await _send_email(email, subject, body)


async def send_officer_response_notification(
    email: str,
    tracking_id: str,
    department: str,
    query: str,
    response_text: str,
    responded_at: str,
):
    """Notify citizen that the department officer has responded to their RTI."""
    subject = f"[RTI-Agent] Official Response Received — {tracking_id}"
    body = (
        f"Hello,\n\n"
        f"An official response has been provided for your RTI request by the target department.\n\n"
        f"**Tracking ID**: {tracking_id}\n"
        f"**Responding Department**: {department}\n"
        f"**Response Timestamp**: {responded_at}\n\n"
        f"**Your Request/Query**:\n{query}\n\n"
        f"**Department Response**:\n{response_text}\n\n"
        f"This request has been successfully closed and marked as completed. You can refer to this email for your records.\n\n"
        f"Thank you for using the RTI-Agent system."
    )
    if email:
        await _send_email(email, subject, body)


