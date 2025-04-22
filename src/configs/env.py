# import os

# from dotenv import load_dotenv

# from pydantic.v1 import BaseSettings
#
# load_dotenv()
#
# LWA_APP_ID = os.getenv("LWA_APP_ID")
# LWA_CLIENT_SECRET = os.getenv("LWA_CLIENT_SECRET")
# SP_API_REFRESH_TOKEN = os.getenv("SP_API_REFRESH_TOKEN")
#


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    LWA_APP_ID: str
    LWA_CLIENT_SECRET: str
    SP_API_REFRESH_TOKEN: str


