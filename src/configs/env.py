from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    LWA_APP_ID: str
    LWA_CLIENT_SECRET: str
    SP_API_REFRESH_TOKEN: str

    API_URL: str
    API_AUTH_TOKEN: str

    LOG_FILE: str
    DATA_FOLDER_PATH: str


