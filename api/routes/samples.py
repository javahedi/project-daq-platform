from fastapi import APIRouter, Depends

from daq_core.storage import SQLiteSampleRepository
from api.dependencies import get_repository


router = APIRouter(
    prefix="/samples",
    tags=["samples"],
)


@router.get("/count")
def get_sample_count(
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    return {
        "count": repo.get_sample_count()
    }





@router.get("/latest")
def get_latest_sample(
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    sample = repo.get_latest_sample()

    if sample is None:
        return {
            "sample": None
        }

    return sample.to_dict()


@router.get("/recent")
def get_recent_samples(
    limit: int = 10,
    repo: SQLiteSampleRepository = Depends(get_repository),
):
    samples = repo.get_recent_samples(limit)

    return [
        sample.to_dict()
        for sample in samples
    ]