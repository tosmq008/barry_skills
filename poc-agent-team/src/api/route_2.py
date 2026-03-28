from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_2")
def get_route_2():
    return {"status": "ok", "route": "2"}
