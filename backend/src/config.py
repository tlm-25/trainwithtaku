import os
from dotenv import load_dotenv
import yaml
from pydantic_settings import BaseSettings
from pydantic import BaseModel, ConfigDict
#get environment variables from dotenv file
load_dotenv()

# Config parameters for project - used across multiple modulesm so twe centralise them here to avoid hardcoding across multiple files and ease of maintenance


#Assumes the config.yaml is stored in the root directory (same level as src and test folders), and we are running the code from root directory. If this is not the case, the YAML_CONFIG_PATH variable should be updated to reflect the correct path to the config.yaml file
YAML_CONFIG_PATH = "config.yaml"

MONGO_DB_CONNECTION_STRING = os.getenv("MONGO_DB_CONNECTION_STRING")

DATABASE_NAME = "trainwithtaku_web"
TEST_DATABASE_NAME = "trainwithtaku_test"

USER_ACCOUNTS_COLLECTION_NAME = "user_accounts"
TEST_USER_ACCOUNTS_COLLECTION_NAME = "user_accounts"

VECTOR_STORE_COLLECTION_NAME = "monyai_context_vectors"



MONGO_VECTOR_INDEX_NAME = "VectorSearchChatbot"
TEST_MONGO_VECTOR_INDEX_NAME = "VectorSearchTest"

CHAT_COLLECTION_NAME= "monyai_chats"
TEST_CHAT_COLLECTION_NAME= "monyai_chats"

TOP_K = 5



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_MODEL_NAME = "text-embedding-3-large"

LLM_VERSION = "gpt-4o-mini"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
TOKEN_BLACKLIST_COLLECTION_NAME = "token_blacklist"

# Test credentials for integration testing
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD")
TEST_CONVERSATION_ID = os.getenv("TEST_CONVERSATION_ID")


class EnvConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    app_environment:str
    log_level:str = "DEBUG"



class EmailConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    mail_from:str
    mail_from_name:str
    mail_from_username:str
    mail_server:str
    mail_port:int
    mail_password:str
    mail_start_tls:bool
    mail_ssl_tls:bool
    test_user_email:str
    dev_email:str
    test_user_password:str
    welcome_email_file_name:str



class DatabaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    mongo_db_connection_string:str
    database_name: str
    test_database_name: str
    user_accounts_collection_name: str
    vector_store_collection_name: str
    chat_collection_name: str
    token_blacklist_collection_name: str
    mongo_vector_index_name: str
    test_mongo_vector_index_name: str



class MonyaiChatbotConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    openai_api_key:str
    embedding_model_name:str
    llm_version:str
    top_k:int
    test_conversation_id:str

class AuthTokenConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    jwt_secret_key:str
    jwt_algorithm:str
    access_token_expire_minutes:int
    refresh_token_expire_days:int





class ProjectConfig(BaseSettings):
    model_config = ConfigDict(frozen=True)
    ''' Represent project configuration parameters as Pydantic model for type validation and ease of access '''
    env_config: EnvConfig
    email: EmailConfig
    database: DatabaseConfig
    chatbot: MonyaiChatbotConfig
    auth: AuthTokenConfig


def load_config_from_yaml(yaml_config_path:str)->ProjectConfig:
    """Load and parse configuration settings from a YAML file.

        :param config_path: Path to the YAML configuration file
        :param env: Environment name to load environment-specific settings
        :return: ProjectConfig instance initialized with parsed configuration
    """
    # Set app environment (dev or prod) - set default to dev  if APP_ENVIRONMENT environment variable not set 
    app_environment = os.getenv("APP_ENVIRONMENT").lower() or "dev"

    # set default log level to DEBUG for dev environment. In production, default to INFO for more readable logs and to conceal secret values that might be included in dev logs
    log_level = "DEBUG" if app_environment in ["dev","development"] else "INFO"
    
    # Configure environment
    env_config = EnvConfig(app_environment=os.getenv("APP_ENVIRONMENT").lower() or "dev",log_level=log_level)

    # Validate that yaml file exists
    if not os.path.exists(yaml_config_path):
        raise FileNotFoundError(f"Could not find find cofig file {yaml_config_path}")
    
    # Validate that yaml file is valid format
    if not yaml_config_path.endswith("yaml") and not yaml_config_path.endswith("yml"):
        raise ValueError("{yaml_config_path} is not a valid yaml file. The file must have a .yml or .yaml extension (e.g. config.yaml)")
    

    # Validate that app environment is valid
    if app_environment not in ["dev","prod","development","production"]:
        raise ValueError(f"{app_environment} is not a valid environment. Environment must be 'dev' (or 'development') or 'prod' (or 'production')")

    #store YAML config as dict
    with open(yaml_config_path) as f:
        
        config_dict = yaml.safe_load(f)
        print(config_dict)

    # inject secrets from environment variables into config dict (these are not stored in YAML for security)
    config_dict["email"]["mail_password"] = os.getenv("MAIL_PASSWORD")
    config_dict["email"]["test_user_password"] = TEST_USER_PASSWORD
    config_dict["email"]["test_user_password"] = TEST_USER_PASSWORD
    config_dict["database"]["mongo_db_connection_string"] = MONGO_DB_CONNECTION_STRING

    config_dict["chatbot"]["openai_api_key"] = OPENAI_API_KEY
    config_dict["chatbot"]["test_conversation_id"] =TEST_CONVERSATION_ID

    config_dict["auth"]["jwt_secret_key"] = JWT_SECRET_KEY
    config_dict["auth"]["jwt_algorithm"] = JWT_ALGORITHM

    config_dict["env_config"]=  env_config.model_dump()
    return ProjectConfig(**config_dict)

    
    
APP_CONFIG = load_config_from_yaml(YAML_CONFIG_PATH)



    

