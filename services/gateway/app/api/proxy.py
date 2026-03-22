"""Reverse proxy router that forwards API requests to backend services."""

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse

from app.core.config import settings

router = APIRouter()

SERVICE_MAP = {
    "/api/v1/auth": settings.AUTH_SERVICE_URL,
    "/api/v1/invite": settings.AUTH_SERVICE_URL,
    "/api/v1/users": settings.AUTH_SERVICE_URL,
    "/api/v1/rooms": settings.ROOM_SERVICE_URL,
    "/api/v1/search": settings.ROOM_SERVICE_URL,
    "/api/v1/bookings": settings.BOOKING_SERVICE_URL,
    "/api/v1/chat": settings.CHAT_SERVICE_URL,
}


async def proxy_request(request: Request, target_base: str) -> Response:
    """Forward a request to a backend service and return its response.

    For SSE (text/event-stream) responses, streams chunks without buffering.
    For normal responses, returns the full response body.

    Args:
        request: The incoming FastAPI request.
        target_base: The base URL of the target backend service.

    Returns:
        The proxied response from the backend service.
    """
    url = f"{target_base}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"

    forward_headers = {
        k: v for k, v in request.headers.items() if k.lower() != "host"
    }
    body = await request.body()

    # Check if the client expects an SSE stream
    accept = request.headers.get("accept", "")
    if "text/event-stream" in accept:
        client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))
        req = client.build_request(
            method=request.method,
            url=url,
            headers=forward_headers,
            content=body,
        )
        resp = await client.send(req, stream=True)
        content_type = resp.headers.get("content-type", "")

        if "text/event-stream" in content_type:

            async def stream_response():
                try:
                    async for chunk in resp.aiter_bytes():
                        yield chunk
                finally:
                    await resp.aclose()
                    await client.aclose()

            return StreamingResponse(
                stream_response(),
                status_code=resp.status_code,
                media_type="text/event-stream",
                headers={
                    k: v
                    for k, v in resp.headers.items()
                    if k.lower()
                    not in ("content-length", "transfer-encoding", "connection")
                },
            )
        else:
            # Not actually SSE, read full response and close
            content = await resp.aread()
            await resp.aclose()
            await client.aclose()
            return Response(
                content=content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
            )

    # Standard non-streaming proxy
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=forward_headers,
            content=body,
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
