from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_5")
def get_route_5():
    return {"status": "ok", "route": "5"}
