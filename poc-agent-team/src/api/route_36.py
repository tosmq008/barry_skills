from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_36")
def get_route_36():
    return {"status": "ok", "route": "36"}
