"""
API v1 - Version 1 API routes
API Version 1 Routes
"""

from fastapi import APIRouter

# Create v1 router
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Import and include all v1 routes here
# For now, we'll keep backward compatibility by including routes at both /api/ and /api/v1/
