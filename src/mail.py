import asyncio
from aiosmtplib import send
from email.message import EmailMessage

async def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = "noreply@example.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    await asyncio.to_thread(
        send, msg, hostname="localhost", port=1025
    )