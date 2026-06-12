import uvicorn

from daq_core.logging_config import setup_logging
from daq_core.runtime import start_daq


if __name__ == "__main__":
    setup_logging()

    start_daq("config.yaml")

    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )