from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_37")
def get_route_37():
    return {"status": "ok", "route": "37"}
