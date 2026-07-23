"""FastAPI application entry point."""

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.core.rate_limit import limiter
from src.api.routes import reactions, comments

# Initialize FastAPI app
app = FastAPI(
    title="Like/Dislike 與留言收集 API",
    version="1.0.0",
    description="無需身份驗證的後端 API，用於收集使用者的讚／不讚反應與留言",
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount routes
app.include_router(reactions.router)
app.include_router(comments.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
