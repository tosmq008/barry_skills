from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_27")
def get_route_27():
    return {"status": "ok", "route": "27"}
