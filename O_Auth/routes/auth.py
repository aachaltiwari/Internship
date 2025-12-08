import urllib.parse
import httpx
from starlette.responses import RedirectResponse, JSONResponse, PlainTextResponse
from starlette.requests import Request

from config import (
    CLIENT_ID, 
    CLIENT_SECRET, 
    REDIRECT_URI, 
    SCOPE, 
    AUTH_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL
)
from token_manager import save_tokens


async def google_auth(request: Request):
    """Step 1: Redirect user to Google Login"""
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


async def google_callback(request: Request):
    """Step 2: Handle Google OAuth callback and save tokens"""
    code = request.query_params.get("code")

    if not code:
        return JSONResponse({"error": "No authorization code"}, status_code=400)

    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data=data)

    tokens = token_response.json()

    if "error" in tokens:
        return JSONResponse({"error": tokens}, status_code=400)

    # Fetch user profile (optional)
    access_token = tokens.get("access_token")
    async with httpx.AsyncClient() as client:
        user_info = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    profile = user_info.json()

    # Save tokens to file
    save_tokens(tokens)

    return PlainTextResponse(
        f"Login Successful!\nWelcome {profile.get('name', 'User')}!\n"
        f"Tokens saved in tokens.json"
    )