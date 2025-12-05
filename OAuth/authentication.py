import os
import urllib.parse
import httpx
import json
import time
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import RedirectResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.requests import Request


load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE")
AUTH_URL = os.getenv("AUTH_URL")

TOKEN_FILE = "tokens.json"


# -----------------------------------------------------
# SAVE TOKENS TO FILE
# -----------------------------------------------------
def save_tokens(tokens):
    data = tokens.copy()
    data["saved_time"] = int(time.time())   # <-- save current time
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------------------------------
# LOAD TOKENS FROM FILE
# -----------------------------------------------------

def load_tokens():
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except:
        return None

# -----------------------------------------------------
# AUTO REFRESH ACCESS TOKEN
# -----------------------------------------------------

async def get_valid_access_token():
    tokens = load_tokens()
    if not tokens:
        return None

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")
    saved_time = tokens.get("saved_time", 0)

    # ---- YOUR EXPIRY FORMULA ----
    current_time = int(time.time())
    expire_at = saved_time + expires_in

    # If still valid → return immediately
    if current_time < expire_at:
        remaining = expire_at - current_time
        print(f"Access token still valid ({remaining}s left)")
        return access_token

    print("Access token expired → refreshing...")

    # ---- REFRESH FLOW ----
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
        )

    new_data = response.json()

    # Update saved tokens
    new_tokens = {
        "access_token": new_data["access_token"],
        "refresh_token": refresh_token,          # refresh token remains same
        "expires_in": new_data["expires_in"],    # e.g. 3599
    }

    save_tokens(new_tokens)
    print("🔄 New access token saved.")

    return new_tokens["access_token"]
# -----------------------------------------------------
# STEP 1 — Redirect user to Google Login
# -----------------------------------------------------
async def google_auth(request):
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent"
    }

    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


# -----------------------------------------------------
# STEP 2 — Google Redirects Back (save tokens to file)
# -----------------------------------------------------
async def google_callback(request):
    code = request.query_params.get("code")

    if not code:
        return JSONResponse({"error": "No authorization code"}, status_code=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=data)

    tokens = token_response.json()

    if "error" in tokens:
        return JSONResponse({"error": tokens}, status_code=400)

    # Fetch profile (optional)
    access_token = tokens.get("access_token")
    async with httpx.AsyncClient() as client:
        user_info = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    profile = user_info.json()

    # Store everything
    save_tokens(tokens)

    return PlainTextResponse("🎉 Login Successful!\nTokens saved in tokens.json")


# -----------------------------------------------------
# STEP 3 — Upload File to Google Drive (auto refresh)
# -----------------------------------------------------
async def upload_to_drive(request: Request):
    access_token = await get_valid_access_token()

    if not access_token:
        return JSONResponse({"error": "Please login first"}, status_code=401)

    # Body contains only file content, NOT token
    body = await request.json()
    file_content = body.get("content", "Hello from Starlette!")
    file_name = body.get("filename", "example.txt")

    metadata = {"name": file_name}

    files = {
        "metadata": ("metadata.json", json.dumps(metadata), "application/json"),
        "file": (file_name, file_content.encode(), "text/plain")
    }

    upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            upload_url,
            headers={"Authorization": f"Bearer {access_token}"},
            files=files
        )

    return JSONResponse(response.json())


# -----------------------------------------------------
# ROUTES
# -----------------------------------------------------
routes = [
    Route("/auth/google", google_auth, methods=["GET"]),
    Route("/auth/callback", google_callback, methods=["GET"]),
    Route("/drive/upload", upload_to_drive, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)
