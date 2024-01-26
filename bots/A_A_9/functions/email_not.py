import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    # Update these values with your email configuration
    sender_email = "denario369@gmail.com"
    receiver_email = "goycoolea23@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465 #465
    smtp_username = "denario369@gmail.com"
    smtp_password = "jqkq crzy gkbh biwx"

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")


# Example usage
# send_email("Test Subject", "Hello, this is a test email.")
