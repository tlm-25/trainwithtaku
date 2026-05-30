from src.email_utils.sender import _create_message, send_email
from src.email_utils.html_utils import HTML_TEMPLATE_FOLDER_PATH
from email.message import EmailMessage
import pytest
import logging
from src.config import APP_CONFIG
# from src.main import app
from src.app_setup import create_app
from fastapi.testclient import TestClient
EMAIL_CONFIG = APP_CONFIG.email

welcome_template_file_name = "welcome.html"

# test recipients (including dev email address and email to myself)
recipients = [EMAIL_CONFIG.dev_email,EMAIL_CONFIG.mail_from]

test_subject = "Welcome"
test_message = "Welcome to TWT Fitness"
test_non_existent_file_path = HTML_TEMPLATE_FOLDER_PATH+ "/" +"non_existent"

test_app = create_app()
# disable rate limiting so that it does not affect testing functionality unless 
#... only skip this line in tests if explicity testing rate limiting
test_app.state.ip_rate_limiter.enabled = False
test_app.state.user_based_rate_limiter.enabled = False
client = TestClient(app=test_app)


@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_create_message_html_only_success():
    '''Test that message created'''
    
    message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name=welcome_template_file_name)
    print(message)
    logging.info(message)
    assert isinstance(message,EmailMessage)
    assert isinstance(message["To"],str)


@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_create_message_text_only_success():
    '''Test that message created'''
    
    message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},text_content=test_message)
    print(message)
    logging.info(message)
    assert isinstance(message,EmailMessage)
    assert isinstance(message["To"],str)



@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_create_message_no_content_to_send_raises_value_error():
    '''Test that correct error raised '''
    


    # simulate case where no text content or html file is passed - make sure 
    with pytest.raises(ValueError,match="No content to send. You must have HTML content or text content to send. Hint: Ensure you set at least one of 'html_file_name' or 'text_content' arguments"):
        message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name=None,text_content=None)



@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_file_non_existent_raises_value_error():
    '''Test that correct error raised when html file does not exist'''

    # simulate case where no text content or html file is passed - make sure 
    with pytest.raises(FileNotFoundError,match=f"Could not find '{test_non_existent_file_path}'"):
        message = await _create_message(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name="non_existent")


@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_send_email():
    '''
        Test that email sends successfully
    
    '''

    email_message = await send_email(recipients=recipients,subject=test_subject,context={"user":EMAIL_CONFIG.test_user_email},html_file_name=welcome_template_file_name)

    assert "success" in email_message["message"].lower()




@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_send_reset_password_link():
    with TestClient(app=test_app) as client:
        # Deliberately do not login - accessed if user forgets password so they won't be logged in 
        # deliberately not handling non-existent emails so that we do not give attackers clues for accounts
        send_password_response= client.post(url="/api/send_change_password_link",json={"email":EMAIL_CONFIG.dev_email})
        
        assert send_password_response.status_code == 200




