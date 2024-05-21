import json

import uvicorn
from constants.auth_code import AUTH_CODE_RESPONSE_FILE_PATH
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/auth_code")
def get_auth_code(code: str, state: str):
    with open(AUTH_CODE_RESPONSE_FILE_PATH, 'w') as f:
        json.dump({"code": code}, f)

    return Response(status_code=200)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
