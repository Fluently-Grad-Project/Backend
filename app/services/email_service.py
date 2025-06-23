import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import EMAIL_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER


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

async def send_verification_code_email(email: str, code: str):
    message = MIMEMultipart()
    message["From"] = EMAIL_FROM
    message["To"] = email
    message["Subject"] = "Password Reset Verification Code"

    body = f"""
    <p>Your password reset verification code is:</p>
    <h2>{code}</h2>
    <p>This code will expire in 15 minutes.</p>
    """

    message.attach(MIMEText(body, "html"))
    send_email_task(message)



def send_email_task(message):
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)
