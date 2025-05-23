import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_USERNAME,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.office365.com",  # ← Correct SMTP for Rich@worcesterflag.com
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_invite_email(name: str, email: str, invite_token: str):
    subject = "You're invited to join the draft!"
    body = f"""
    Hi {name},

    Click this link to set up your account and join the draft:
    {settings.FRONTEND_URL}/invite/{invite_token}
    """
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="plain"
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        logging.exception("Failed to send invite email to %s", email)
        raise
