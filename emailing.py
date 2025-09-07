import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import  load_dotenv
import smtplib

load_dotenv()

def send_email(image_path):
    sender_email = os.getenv("EMAIL")
    sender_password = os.getenv("EMAIL_API_KEY")
    receiver_email = os.getenv("EMAIL")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Security Alert: Object Detected!"

    body = "An object has been detected in the monitored area. Please review the attached image."
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read(), name=os.path.basename(image_path))
            msg.attach(img)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print('Email sent successfully with attachment!')
    except Exception as e:
        print(f"Email sending failed: {e}")