from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_25")
def get_route_25():
    return {"status": "ok", "route": "25"}
