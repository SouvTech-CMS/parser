import json

import uvicorn
from constants.auth_code import AUTH_CODE_RESPONSE_FILE_PATH
from fastapi import FastAPI, Response
from utils.json_file_handler import write_json

app = FastAPI()


@app.get("/auth_code")
def get_auth_code(code: str, state: str):
    write_json(AUTH_CODE_RESPONSE_FILE_PATH, {"code": code})

    return Response(status_code=200)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
