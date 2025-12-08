import json
import time
import httpx
from config import TOKEN_FILE, CLIENT_ID, CLIENT_SECRET, GOOGLE_TOKEN_URL


def save_tokens(tokens):
    """Save tokens to file with timestamp"""
    data = tokens.copy()
    data["saved_time"] = int(time.time())
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_tokens():
    """Load tokens from file"""
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


async def get_valid_access_token():
    """Get valid access token, refresh if expired"""
    tokens = load_tokens()
    if not tokens:
        return None

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")
    saved_time = tokens.get("saved_time", 0)

    # Check if token is still valid
    current_time = int(time.time())
    expire_at = saved_time + expires_in

    if current_time < expire_at:
        remaining = expire_at - current_time
        print(f"Access token still valid ({remaining}s left)")
        return access_token

    # Token expired, refresh it
    print("Access token expired → refreshing...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
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
        "refresh_token": refresh_token,
        "expires_in": new_data["expires_in"],
    }

    save_tokens(new_tokens)
    print("New access token saved.")

    return new_tokens["access_token"]