from starlette.applications import Starlette
from starlette.middleware import Middleware
from routes.urls import routes
from middlewares import LoggingMiddleware, RateLimitMiddleware

# Create Starlette application
app = Starlette(
    debug=True,
    routes=routes,
    middleware=[
        Middleware(LoggingMiddleware),
        Middleware(RateLimitMiddleware)
    ]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)