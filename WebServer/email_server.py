import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = username

    def send_email(self, recipient_email, subject, message, html_table=None):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Create the plain-text and HTML version of your message
        text_part = MIMEText(message, 'plain')
        html_part = MIMEText(f"{message}<br><br>{html_table}", 'html')

        # Attach parts into message container.
        msg.attach(text_part)
        if html_table:
            msg.attach(html_part)


        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email. Error: {str(e)}")