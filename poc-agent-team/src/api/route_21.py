from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_21")
def get_route_21():
    return {"status": "ok", "route": "21"}
