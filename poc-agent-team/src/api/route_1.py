from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_1")
def get_route_1():
    return {"status": "ok", "route": "1"}
