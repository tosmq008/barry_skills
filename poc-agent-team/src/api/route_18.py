from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_18")
def get_route_18():
    return {"status": "ok", "route": "18"}
