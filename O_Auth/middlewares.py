import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from config import RATE_LIMIT, RATE_PERIOD, request_store

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()

        # Log incoming request
        print(f"{request.method} {request.url.path}")

        # Process the request
        response = await call_next(request)

        # Log response time
        duration = (time.time() - start) * 1000
        print(f"{request.method} {request.url.path} - {round(duration, 2)} ms")
        print("Yes yes yes yes done")

        return response
    


# -------------------------------
# Rate Limiting Middleware
# -------------------------------
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client_ip = request.client.host

        now = time.time()

        # Create list for IP if not exists
        if client_ip not in request_store:
            request_store[client_ip] = []

        # Remove old timestamps older than RATE_PERIOD
        request_store[client_ip] = [
            ts for ts in request_store[client_ip]
            if now - ts < RATE_PERIOD
        ]

        # Check if limit reached
        if len(request_store[client_ip]) >= RATE_LIMIT:
            return JSONResponse(
                {"error": "Rate limit exceeded. Try again later."},
                status_code=429
            )

        # Add this request timestamp
        request_store[client_ip].append(now)

        # Continue to the endpoint
        return await call_next(request)
