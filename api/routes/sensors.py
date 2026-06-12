
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
    return { "sensors": repo.get_sensor_ids() }


@router.get("/{sensor_id}/samples")
def get_samples_for_sensor(
    sensor_id: str,
    limit: int = 10,
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    samples = repo.get_samples_by_sensor(
        sensor_id=sensor_id,
        limit=limit,
    )

    return [ sample.to_dict() for sample in samples]


@router.get("/{sensor_id}/statistics")
def get_sensor_statistics(
    sensor_id: str,
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    return repo.get_sensor_statistics(sensor_id)


@router.get("/details")
def get_sensor_details(
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    return {
        "sensors": repo.get_sensor_details()
    }