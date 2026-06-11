from fastapi import FastAPI

from daq_core.storage import SQLiteSampleRepository


app = FastAPI()

repo = SQLiteSampleRepository("data/daq.db")


@app.get("/status")
def status():
    return {
        "status": "running"
    }


@app.get("/samples/count")
def get_sample_count():
    return {
        "count": repo.get_sample_count()
    }

@app.get("/samples/latest")
def get_latest_sample():

    sample = repo.get_latest_sample()

    if sample is None:
        return {
            "sample": None
        }

    return sample.to_dict()