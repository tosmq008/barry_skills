from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_4")
def get_route_4():
    return {"status": "ok", "route": "4"}
