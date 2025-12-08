from starlette.routing import Route
from routes.auth import google_auth, google_callback
from routes.drive import upload_to_drive

# Define all routes
routes = [
    Route("/auth/google", google_auth, methods=["GET"]),
    Route("/auth/callback", google_callback, methods=["GET"]),
    Route("/drive/upload", upload_to_drive, methods=["POST"]),
]