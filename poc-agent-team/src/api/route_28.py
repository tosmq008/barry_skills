from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_28")
def get_route_28():
    return {"status": "ok", "route": "28"}
