from email.mime.multipart import MIMEMultipart

import boto3
from botocore.exceptions import ClientError


class EmailClient(object):
    """
    base class of email client
    """
    def send(self, message: MIMEMultipart) -> None:
        """
        send email with the message
        """
        raise NotImplementedError


class SESEmailClient(EmailClient):
    """
    email client using SES
    """
    def __init__(self):
        self.client = boto3.client('ses', region_name='us-east-1')

    def send(self, message: MIMEMultipart) -> None:
        try:
            response = self.client.send_raw_email(
                Source=message['from'],
                Destinations=message['to'].split(','),
                RawMessage={'Data': message.as_string()},
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
