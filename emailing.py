import mimetypes
import os
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import  load_dotenv
import smtplib

load_dotenv()

def send_email_solution(image_path):
    print('email started')
    sender_email = os.getenv("EMAIL")
    sender_password = os.getenv("EMAIL_API_KEY")
    receiver_email = os.getenv("EMAIL")

    email_message = EmailMessage()
    email_message["Subject"] = "We captured something"
    email_message.set_content("Hey something showed up")

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"  # fallback
    maintype, subtype = mime_type.split("/")

    with open(image_path, "rb") as file:
        email_message.add_attachment(file.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(image_path))

    with smtplib.SMTP("smtp.gmail.com", 587) as gmail:
        gmail.starttls()
        gmail.login(sender_email, sender_password)
        email_message["From"] = sender_email
        email_message["To"] = receiver_email
        gmail.send_message( email_message)
        gmail.quit()
    print('email sent')

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

if __name__ == "__main__":
    send_email_solution("sent/48.png")