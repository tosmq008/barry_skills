from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_20")
def get_route_20():
    return {"status": "ok", "route": "20"}
