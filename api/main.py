from fastapi import FastAPI

from api.routes.status import router as status_router
from api.routes.samples import router as samples_router


app = FastAPI(
    title="DAQ Platform API",
    version="0.1.0",
)

app.include_router(status_router)
app.include_router(samples_router)