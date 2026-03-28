from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_8")
def get_route_8():
    return {"status": "ok", "route": "8"}
