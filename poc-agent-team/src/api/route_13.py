from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_13")
def get_route_13():
    return {"status": "ok", "route": "13"}
