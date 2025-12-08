import os
from dotenv import load_dotenv

load_dotenv()

# Google OAuth Configuration
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE")
AUTH_URL = os.getenv("AUTH_URL")

# Token Storage
TOKEN_FILE = "tokens.json"

# Google API URLs
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"

RATE_LIMIT = 2              # allowed requests
RATE_PERIOD = 60             # per 60 seconds (1 minute)
request_store = {}           # IP → [timestamps]