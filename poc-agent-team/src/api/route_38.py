from fastapi import APIRouter
router = APIRouter()

@router.get("/api/v1/route_38")
def get_route_38():
    return {"status": "ok", "route": "38"}
