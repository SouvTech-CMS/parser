import json

from flask import Flask, request

from constants.auth_code import AUTH_RESPONSE_FILE_PATH

app = Flask(__name__)


@app.route("/redirect", methods=['GET'])
def redirect():
    auth_code = request.args.get('code')

    if not auth_code:
        auth_code = ""

    with open(AUTH_RESPONSE_FILE_PATH, 'w') as f:
        json.dump({
            "auth_code": auth_code,
        }, f)

    return {"status": "success"}, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
