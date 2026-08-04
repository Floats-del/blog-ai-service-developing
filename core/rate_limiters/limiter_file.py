from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(
    key_func=get_remote_address,

    # Default limit for every endpoint
    # default_limits=["1/minute"],

    # No global app-wide limit for now
    application_limits=[],

    # Include rate-limit headers in responses
    headers_enabled=True,

    # Use the default strategy (leave as None) uses fixed window by defualt 
    strategy=None, #we can use any in: ["fixed-window", "moving-window", "sliding-window-counter"]

    # Store counters in Redis
    storage_uri="redis://localhost:6379",

    # No special Redis options needed locally
    storage_options={},

    # Automatically check limits on decorated routes
    auto_check=True,

    # Raise errors normally instead of silently ignoring them
    swallow_errors=False,

    # If Redis dies, temporarily fall back to memory
    in_memory_fallback=["1/minute"],

    # Enable that fallback
    in_memory_fallback_enabled=True,

    # Return Retry-After as seconds
    retry_after="delta",
)