from fastapi import APIRouter

# Main API Router
router = APIRouter()

# Hier werden später die einzelnen Subrouter eingebunden:
# router.include_router(members.router, prefix="/members", tags=["members"])
# router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
# router.include_router(pto.router, prefix="/pto", tags=["pto"])
# router.include_router(holidays.router, prefix="/holidays", tags=["holidays"])

# Placeholder API Route
@router.get("/status")
async def api_status():
    """API Status Endpoint"""
    return {
        "api_status": "ready",
        "message": "Capacity Planner API v1.0.0"
    }
