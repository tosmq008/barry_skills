from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_26")
def get_route_26():
    return {"status": "ok", "route": "26"}
