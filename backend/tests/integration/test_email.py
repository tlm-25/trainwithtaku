from src.email_utils.sender import _create_message, send_email
from src.email_utils.html_utils import HTML_TEMPLATE_FOLDER_PATH
from email.message import EmailMessage
import pytest
import logging
from src.config import APP_CONFIG

EMAIL_CONFIG = APP_CONFIG.email

welcome_template_file_name = "welcome.html"

# test recipients (including dev email address and email to myself)
recipients = [EMAIL_CONFIG.dev_email,EMAIL_CONFIG.mail_from]

test_subject = "Welcome"
test_message = "Welcome to TWT Fitness"
test_non_existent_file_path = HTML_TEMPLATE_FOLDER_PATH+ "/" +"non_existent"



@pytest.mark.asyncio
async def test_create_message_html_only_success():
    '''Test that message created'''
    
    message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name=welcome_template_file_name)
    print(message)
    logging.info(message)
    assert isinstance(message,EmailMessage)
    assert isinstance(message["To"],str)

@pytest.mark.asyncio
async def test_create_message_text_only_success():
    '''Test that message created'''
    
    message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},text_content=test_message)
    print(message)
    logging.info(message)
    assert isinstance(message,EmailMessage)
    assert isinstance(message["To"],str)


@pytest.mark.asyncio
async def test_create_message_no_content_to_send_raises_value_error():
    '''Test that correct error raised '''
    


    # simulate case where no text content or html file is passed - make sure 
    with pytest.raises(ValueError,match="No content to send. You must have HTML content or text content to send. Hint: Ensure you set at least one of 'html_file_name' or 'text_content' arguments"):
        message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name=None,text_content=None)


@pytest.mark.asyncio
async def test_file_non_existent_raises_value_error():
    '''Test that correct error raised when html file does not exist'''

    # simulate case where no text content or html file is passed - make sure 
    with pytest.raises(FileNotFoundError,match=f"Could not find '{test_non_existent_file_path}'"):
        message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name="non_existent")

@pytest.mark.asyncio
async def test_send_email():
    '''
        Test that email sends successfully
    
    '''

    email_message = await send_email(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name=welcome_template_file_name)

    assert "success" in email_message["message"].lower()