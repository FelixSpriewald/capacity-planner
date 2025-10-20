from fastapi import APIRouter

from app.api import members, sprints, roster, availability

# Main API Router
router = APIRouter()

# Constants
SPRINTS_PREFIX = "/sprints"

# Sub-Router einbinden
router.include_router(members.router, prefix="/members", tags=["members"])
router.include_router(sprints.router, prefix=SPRINTS_PREFIX, tags=["sprints"])
router.include_router(roster.router, prefix=SPRINTS_PREFIX, tags=["roster"])  # /sprints/{id}/roster
router.include_router(availability.router, prefix=SPRINTS_PREFIX, tags=["availability"])  # /sprints/{id}/availability

# Status API Route
@router.get("/status")
async def api_status():
    """API Status Endpoint"""
    return {
        "api_status": "ready",
        "message": "Capacity Planner API v1.0.0",
        "endpoints": [
            "GET /api/members - List all members",
            "POST /api/members - Create member",
            "GET /api/sprints - List all sprints",
            "POST /api/sprints - Create sprint",
            "PATCH /api/sprints/{id} - Update sprint",
            "GET /api/sprints/{id}/roster - Get sprint roster",
            "POST /api/sprints/{id}/roster - Add member to sprint",
            "PUT /api/sprints/{id}/roster/{member_id} - Update roster entry",
            "DELETE /api/sprints/{id}/roster/{member_id} - Remove member from sprint",
            "GET /api/sprints/{id}/availability - Get availability matrix",
            "PATCH /api/sprints/{id}/availability - Set single override",
            "PATCH /api/sprints/{id}/availability/bulk - Bulk update overrides"
        ]
    }
