import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import List, Dict, Any
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Daily Job Application Reminders</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
        .header { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px; }
        .reminder-item { margin-bottom: 15px; padding: 15px; border-left: 4px solid #22c55e; background-color: #f0fdf4; }
        .overdue { border-left-color: #ef4444; background-color: #fef2f2; }
        .company { font-weight: bold; color: #0f172a; }
        .role { color: #475569; }
        .action { margin-top: 5px; font-style: italic; }
        .due-date { color: #64748b; font-size: 0.9em; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 0.9em; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 4px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Daily Job Application Reminders</h1>
            <p>Hi {{ user_name }},</p>
            <p>You have {{ total_items }} action{{ 's' if total_items != 1 else '' }} due today:</p>
        </div>

        {% for item in items %}
        <div class="reminder-item {% if item.is_overdue %}overdue{% endif %}">
            <div class="company">{{ item.company }}</div>
            <div class="role">{{ item.role_title }}</div>
            <div class="action">{{ item.next_action }}</div>
            <div class="due-date">
                Due: {{ item.next_action_due }}
                {% if item.is_overdue %}<strong>(OVERDUE)</strong>{% endif %}
            </div>
            <a href="{{ base_url }}/applications/{{ item.id }}" class="btn">View Application</a>
        </div>
        {% endfor %}

        <div class="footer">
            <p>Manage your job applications at <a href="{{ base_url }}">Job Tracker</a></p>
            <p><a href="{{ base_url }}/settings">Update your reminder preferences</a></p>
        </div>
    </div>
</body>
</html>
"""

TEXT_TEMPLATE = """
Daily Job Application Reminders

Hi {{ user_name }},

You have {{ total_items }} action{{ 's' if total_items != 1 else '' }} due today:

{% for item in items %}
{{ item.company }} - {{ item.role_title }}
Action: {{ item.next_action }}
Due: {{ item.next_action_due }}{% if item.is_overdue %} (OVERDUE){% endif %}
View: {{ base_url }}/applications/{{ item.id }}

{% endfor %}

Manage your job applications at {{ base_url }}
Update your reminder preferences at {{ base_url }}/settings
"""


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASS
        self.email_from = settings.EMAIL_FROM
        self.base_url = settings.APP_BASE_URL

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str):
        """Send an email."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email

            # Create text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_daily_reminders(self, user_email: str, user_name: str, reminder_items: List[Dict[str, Any]]):
        """Send daily reminder email."""
        if not reminder_items:
            return True

        # Prepare template data
        template_data = {
            'user_name': user_name,
            'total_items': len(reminder_items),
            'items': reminder_items,
            'base_url': self.base_url
        }

        # Render templates
        html_template = Template(EMAIL_TEMPLATE)
        text_template = Template(TEXT_TEMPLATE)

        html_content = html_template.render(**template_data)
        text_content = text_template.render(**template_data)

        subject = f"Daily Reminders - {len(reminder_items)} action{'s' if len(reminder_items) != 1 else ''} due"

        return self.send_email(user_email, subject, html_content, text_content)


email_service = EmailService()
