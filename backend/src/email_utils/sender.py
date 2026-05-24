# from src.web_utils import render_html_template
from src.config import APP_CONFIG
from src.email_utils.html_utils import render_html_template

import aiosmtplib
from aiosmtplib import send

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email.message import EmailMessage
import logging


EMAIL_APP_CONFIG = APP_CONFIG.email
WELCOME_EMAIL_FILE_NAME = EMAIL_APP_CONFIG.welcome_email_file_name



async def _create_message(recipients:list[str],subject:str,context:dict=None,html_file_name:str=None,text_content:str=None) -> EmailMessage:
    '''
    Helper function to create an email message object with provided recipients, subject, and body.

    Documentation reference - https://aiosmtplib.readthedocs.io/en/latest/usage.html#sending-messages

    :param recipients: list of email addresses to send to
    :param subject: subject of the email
    :param html_file_name (optional): name of the html file we want to read (assumes the file exists in template_folder_path)
    :return: EmailMessage object ready to be sent

    '''
    message = EmailMessage()
    message["From"] = EMAIL_APP_CONFIG.mail_from_name
    # Reference for sending to multiple recipients - https://stackoverflow.com/questions/8856117/how-to-send-email-to-multiple-recipients-using-python-smtplib
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    if not (html_file_name or text_content):
        raise ValueError("No content to send. You must have HTML content or text content to send. Hint: Ensure you set at least one of 'html_file_name' or 'text_content' arguments")

    if text_content:
        message.set_content(text_content)

    if html_file_name:
        html_content = render_html_template(html_file_name=html_file_name,context=context)
        message.add_alternative(html_content,subtype="html")

    return message


async def send_email(recipients:list[str],subject:str,context:dict=None,html_file_name:str=None,text_content:str=None):
    '''
    Send an email to one or more recipients with optional plain text and/or HTML content.

    At least one of html_file_name or text_content must be provided.
    If both are provided, the email is sent as multipart — clients that cannot render HTML fall back to plain text.

    :param recipients: list of email addresses to send to
    :param subject: subject line of the email
    :param context: template variables to inject into the HTML template (e.g. {"name": "Alice"} replaces {{ name }})
    :param html_file_name: name of the HTML template file to render and attach (must exist in the 'templates' folder)
    :param text_content: plain-text body of the email
    '''
    email_message = await _create_message(recipients=recipients,subject=subject,context=context,html_file_name=html_file_name,text_content=text_content)

    logging.info(f"sending email to {email_message['To']}")
    await send(email_message,
            hostname=EMAIL_APP_CONFIG.mail_server,
            port=EMAIL_APP_CONFIG.mail_port,
            username=EMAIL_APP_CONFIG.mail_from,
            password=EMAIL_APP_CONFIG.mail_password.get_secret_value(),
            recipients=recipients,
            start_tls=EMAIL_APP_CONFIG.mail_start_tls)
    
    return {"message":"Successfully sent email"}