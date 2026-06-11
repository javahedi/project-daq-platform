
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


@router.get("/{sensor_id}/samples")
def get_samples_for_sensor(
    sensor_id: str,
    limit: int = 100,
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    samples = repo.get_samples_by_sensor(
        sensor_id=sensor_id,
        limit=limit,
    )

    return [
        sample.to_dict()
        for sample in samples
    ]