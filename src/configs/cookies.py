import json

with open("./cookies.json") as f:
    COOKIES = json.load(f)

print(f"Cookies: {COOKIES}")
