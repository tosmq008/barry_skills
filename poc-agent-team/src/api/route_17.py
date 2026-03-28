from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_17")
def get_route_17():
    return {"status": "ok", "route": "17"}
