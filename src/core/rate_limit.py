"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter with in-memory storage
# Uses request.client.host as the key (per-IP rate limiting)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["3/minute"],  # 3 requests per minute per IP
    storage_uri=None,  # Use in-memory storage (default)
)
