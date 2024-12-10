import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailServer:
    def __init__(self, smtp_server, port, username, password):
        """
        Initializes the email server configuration.

        Args:
            smtp_server (str): The SMTP server address.
            port (int): The port number to use for the SMTP server.
            username (str): The username for the email account.
            password (str): The password for the email account.
        """
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.server = None

    def connect(self):
        """
        Establishes a connection to the SMTP server using the provided server address and port.
        Initiates TLS encryption and logs in with the specified username and password.

        Raises:
            smtplib.SMTPException: If there is an issue with the SMTP connection or authentication.
        """
        self.server = smtplib.SMTP(self.smtp_server, self.port)
        self.server.starttls()
        self.server.login(self.username, self.password)

    def send_email(self, to_email, subject, body):
        """
        Sends an email using the configured SMTP server.

        Args:
            to_email (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body content of the email.

        Returns:
            None
        """
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        self.server.sendmail(self.username, to_email, msg.as_string())

    def disconnect(self):
        """
        Disconnects from the email server if a connection exists.

        This method checks if the server attribute is set, and if so, it calls the
        quit method on the server to terminate the connection.
        """
        if self.server:
            self.server.quit()

# Example usage:
# email_server = EmailServer('smtp.example.com', 587, 'your_email@example.com', 'your_password')
# email_server.connect()
# email_server.send_email('recipient@example.com', 'Test Subject', 'This is a test email.')
# email_server.disconnect()