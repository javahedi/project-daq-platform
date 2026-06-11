
from fastapi import APIRouter, Depends

from daq_core.storage import SQLiteSampleRepository
from api.dependencies import get_repository

router = APIRouter(
    prefix="/sensors",
    tags=["sensors"],
)



@router.get("")
def get_sensor_ids(
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    return {
    "sensors": repo.get_sensor_ids()
}