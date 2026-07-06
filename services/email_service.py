"""
Email Notification Service - SMTP email delivery
"""

from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from services.logging_service import logger

load_dotenv()


class EmailService:
    """Email notification service"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Elder Company")
        
        self.email_enabled = bool(self.smtp_user and self.smtp_password)
        
        if not self.email_enabled:
            logger.log_warning("SMTP credentials not found. Email notifications will not work.")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            
        Returns:
            Whether send succeeded
        """
        if not self.email_enabled:
            logger.log_warning("Email service not enabled. Email not sent.")
            return False
        
        if not to_email:
            logger.log_warning("Recipient email is empty. Email not sent.")
            return False
        
        try:
            import smtplib
            
            # Build message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Plain text part
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML part (optional)
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.log_info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.log_error(e, {"action": "send_email", "to_email": to_email})
            return False
    
    def send_email_batch(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Send email to multiple recipients
        
        Args:
            to_emails: Recipient email list
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            
        Returns:
            Send results dict {email: success}
        """
        results = {}
        
        for email in to_emails:
            success = self.send_email(email, subject, body, html_body)
            results[email] = success
        
        return results


# Global instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service instance (singleton)"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
