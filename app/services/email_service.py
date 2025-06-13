import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_PASSWORD, SMTP_USER, EMAIL_FROM


async def send_verification_email(email: str, verification_link: str):
    message = MIMEMultipart()
    message["From"] = EMAIL_FROM
    message["To"] = email
    message["Subject"] = "Email verification code"

    body = f"""
    <p>Please click the link below to verify your email:</p>
    <p><a href="{verification_link}">{verification_link}</a></p>
    """

    message.attach(MIMEText(body, "html"))

    send_email_task(message)


def send_email_task(message):
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)
