"""
Rate limiting middleware to prevent abuse.
Implements 100 requests per minute per user as per requirements.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    Limits requests to 100 per minute per user/IP.
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = datetime.utcnow()
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client.
        Uses user_id from token if available, otherwise IP address.
        """
        # Try to get user_id from request state (set by auth dependency)
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        return f"ip:{request.client.host}"
    
    def _cleanup_old_requests(self):
        """Remove request timestamps older than 1 minute."""
        now = datetime.utcnow()
        if (now - self.last_cleanup).seconds < self.cleanup_interval:
            return
        
        cutoff = now - timedelta(minutes=1)
        for client_id in list(self.request_counts.keys()):
            self.request_counts[client_id] = [
                timestamp for timestamp in self.request_counts[client_id]
                if timestamp > cutoff
            ]
            # Remove empty entries
            if not self.request_counts[client_id]:
                del self.request_counts[client_id]
        
        self.last_cleanup = now
    
    def _is_rate_limited(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limit.
        
        Returns:
            Tuple of (is_limited, remaining_requests)
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        # Get requests in the last minute
        recent_requests = [
            timestamp for timestamp in self.request_counts[client_id]
            if timestamp > cutoff
        ]
        
        # Update the list
        self.request_counts[client_id] = recent_requests
        
        # Check if limit exceeded
        is_limited = len(recent_requests) >= self.requests_per_minute
        remaining = max(0, self.requests_per_minute - len(recent_requests))
        
        return is_limited, remaining
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/api/v1/"]:
            return await call_next(request)
        
        # Periodic cleanup
        self._cleanup_old_requests()
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        is_limited, remaining = self._is_rate_limited(client_id)
        
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": f"Rate limit: {self.requests_per_minute} requests per minute",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int((datetime.utcnow() + timedelta(minutes=1)).timestamp())),
                    "Retry-After": "60"
                }
            )
        
        # Record this request
        self.request_counts[client_id].append(datetime.utcnow())
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        
        return response
