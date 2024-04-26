from pydantic import BaseModel

from configs.env import DATA_FOLDER_PATH

AUTH_RESPONSE_FILE_PATH = f"{DATA_FOLDER_PATH}/auth-response.json"


class AuthResponse(BaseModel):
    code: str
