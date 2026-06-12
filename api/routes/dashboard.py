from fastapi import APIRouter
from fastapi.responses import FileResponse



router = APIRouter(
    tags=["dashboard"],
)


@router.get("/dashboard")
def dashboard():
    return FileResponse("dashboard/index.html")
    

