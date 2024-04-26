import os

from dotenv import load_dotenv

load_dotenv()

ETSY_API_KEY = os.getenv('ETSY_API_KEY')
ETSY_API_SHARED_SECRET = os.getenv('ETSY_API_SHARED_SECRET')
ETSY_API_REDIRECT_URL = os.getenv('ETSY_API_REDIRECT_URL')

CODE_VERIFIER = os.getenv('CODE_VERIFIER')

API_URL = os.getenv('API_URL')

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH')
