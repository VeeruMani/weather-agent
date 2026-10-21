import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# Single user
# def send_weather_email(city: str, weather_output: str) -> None:

#     sender = os.getenv("EMAIL_SENDER")
#     password = os.getenv("EMAIL_PASSWORD")
#     receiver = os.getenv("EMAIL_RECEIVER")

#     if not all([sender, password, receiver]):
#         raise ValueError("Email configuration is missing in .env")

#     message = EmailMessage()

#     message["From"] = sender
#     message["To"] = receiver
#     message["Subject"] = f"Weather Report - {city}"

#     message.set_content(weather_output)

#     with smtplib.SMTP_SSL(
#         "smtp.gmail.com", 465, timeout=20
#     ) as smtp:

#         smtp.login(sender, password)
#         smtp.send_message(message)

#     print("Email sent successfully!")

#multiple users
import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_weather_email(city: str, weather_output: str) -> None:

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    receivers = [
        email.strip()
        for email in os.getenv("EMAIL_RECEIVERS", "").split(",")
        if email.strip()
    ]

    if not sender or not password or not receivers:
        raise ValueError("Missing email configuration in .env")

    message = EmailMessage()

    message["From"] = sender
    message["To"] = ", ".join(receivers)
    message["Subject"] = f"Weather Report - {city}"
    message.set_content(weather_output)

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as smtp:

            smtp.login(sender, password)
            smtp.send_message(message)

        print(f"\nEmail submitted for {len(receivers)} recipients.")

        for receiver in receivers:
            print(f"  - {receiver}")

    except smtplib.SMTPException as error:
        print(f"Failed to send email: {error}")
        raise