from fastapi_mail import FastMail, ConnectionConfig
import yaml
from src.config import APP_CONFIG

EMAIL_APP_CONFIG = APP_CONFIG.email_config

email_setup_config = ConnectionConfig(
    MAIL_FROM_NAME=EMAIL_APP_CONFIG.mail_from_name,
    MAIL_USERNAME= EMAIL_APP_CONFIG.mail_from_username,
    MAIL_PASSWORD = EMAIL_APP_CONFIG.mail_password,
    MAIL_FROM = EMAIL_APP_CONFIG.mail_from,
    MAIL_SERVER = EMAIL_APP_CONFIG.mail_server,
    MAIL_STARTTLS= EMAIL_APP_CONFIG.mail_start_tls,
    MAIL_SSL_TLS=EMAIL_APP_CONFIG.mail_ssl_tls
)


# mail object - this object is where we will acces obvjects that help us send emails
mail = FastMail()

