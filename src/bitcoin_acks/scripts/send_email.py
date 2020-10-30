import os
import smtplib

import structlog


class EmailNotifier(object):
    """Class for handling gmail notifications
    """

    def __init__(self):
        self.logger = structlog.get_logger()
        self.smtp_server = os.environ['SMTP_URL']
        self.username = os.environ['SMTP_USERNAME']
        self.password = os.environ['SMTP_PASSWORD']
        self.destination_address = os.environ['SMTP_ADDRESS']

    def notify(self, message):
        """Sends the message.
        Args:
            message (str): The message to send.
        Returns:
            dict: A dictionary containing the result of the attempt to send the email.
        """

        header = 'From: %s\n' % self.username
        header += 'To: %s\n' % self.destination_address
        header += 'Content-Type: text/plain\n'
        header += 'Subject: ACKs\n\n'
        message = header + message

        smtp_handler = smtplib.SMTP(self.smtp_server)
        smtp_handler.starttls()
        smtp_handler.login(self.username, self.password)
        result = smtp_handler.sendmail(self.username, self.destination_address, message)
        smtp_handler.quit()
        return result


email = EmailNotifier()
