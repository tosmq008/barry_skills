from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_12")
def get_route_12():
    return {"status": "ok", "route": "12"}
