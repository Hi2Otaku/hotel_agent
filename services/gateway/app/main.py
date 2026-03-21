"""HotelBook Gateway Service - Reverse proxy to backend services."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.booking import router as booking_router
from app.api.proxy import router as proxy_router
from app.api.search import router as search_router
from app.api.reports import router as reports_router
from app.api.staff import router as staff_router

app = FastAPI(title="HotelBook Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)   # BFF search -- specific routes take precedence
app.include_router(booking_router)  # BFF booking -- before proxy
app.include_router(staff_router)    # BFF staff -- before proxy
app.include_router(reports_router)  # BFF reports -- before proxy
app.include_router(proxy_router)    # catch-all proxy


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "gateway"}
