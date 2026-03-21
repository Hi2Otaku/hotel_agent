"""Reverse proxy router that forwards API requests to backend services."""

import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import settings

router = APIRouter()

SERVICE_MAP = {
    "/api/v1/auth": settings.AUTH_SERVICE_URL,
    "/api/v1/invite": settings.AUTH_SERVICE_URL,
    "/api/v1/users": settings.AUTH_SERVICE_URL,
    "/api/v1/rooms": settings.ROOM_SERVICE_URL,
    "/api/v1/search": settings.ROOM_SERVICE_URL,
    "/api/v1/bookings": settings.BOOKING_SERVICE_URL,
}


async def proxy_request(request: Request, target_base: str) -> Response:
    """Forward a request to a backend service and return its response.

    Args:
        request: The incoming FastAPI request.
        target_base: The base URL of the target backend service.

    Returns:
        The proxied response from the backend service.
    """
    async with httpx.AsyncClient() as client:
        url = f"{target_base}{request.url.path}"
        if request.url.query:
            url += f"?{request.url.query}"
        resp = await client.request(
            method=request.method,
            url=url,
            headers={
                k: v for k, v in request.headers.items() if k.lower() != "host"
            },
            content=await request.body(),
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
        )


@router.api_route(
    "/api/v1/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def gateway_proxy(request: Request, path: str):
    """Route all /api/v1/* requests to the appropriate backend service."""
    full_path = f"/api/v1/{path}"
    for prefix, service_url in SERVICE_MAP.items():
        if full_path.startswith(prefix):
            return await proxy_request(request, service_url)
    return Response(
        content='{"detail": "Service not found"}',
        status_code=404,
        media_type="application/json",
    )
