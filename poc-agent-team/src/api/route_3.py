from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_3")
def get_route_3():
    return {"status": "ok", "route": "3"}
