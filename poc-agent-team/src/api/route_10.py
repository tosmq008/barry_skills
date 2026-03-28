from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_10")
def get_route_10():
    return {"status": "ok", "route": "10"}
