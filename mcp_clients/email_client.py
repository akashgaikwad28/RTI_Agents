# email_client.py - auto-generated
"""
email_client.py
----------------
Handles RTI email communication. In MVP, this client simulates sending
emails to departments and logs them for auditing. Supports easy
migration to real SMTP in production.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logger import logger
from utils.exception_handler import exception_handler
from config.settings import settings


class EmailClient:
    """
    Handles email sending for RTI communication.
    - In MVP: Simulates email sending (logs + mock confirmation).
    - In production: Can use Gmail SMTP or SendGrid API.
    """

    def __init__(self, simulate_mode: bool = True):
        self.simulate_mode = simulate_mode
        if not simulate_mode:
            # Configure SMTP for Gmail or other providers
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.sender_email = settings.SENDER_EMAIL
            self.sender_password = settings.SENDER_PASSWORD

        logger.info(
            f"📧 EmailClient initialized (simulate_mode={simulate_mode})"
        )

    @exception_handler
    def send_email(self, recipient: str, subject: str, body: str) -> dict:
        """
        Sends (or simulates) an email.
        Returns a response dict with status and details.
        """
        try:
            if self.simulate_mode:
                logger.info(
                    f"📨 Simulated sending email to {recipient} | Subject: {subject}"
                )
                logger.debug(f"Email body: {body}")
                return {
                    "status": "simulated",
                    "recipient": recipient,
                    "subject": subject,
                }

            # Real SMTP sending mode
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"✅ Email successfully sent to {recipient}")
            return {"status": "sent", "recipient": recipient, "subject": subject}

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            raise


# Singleton instance for shared usage
email_client = EmailClient(simulate_mode=True)
