from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from api.routes.status import router as status_router
from api.routes.samples import router as samples_router
from api.routes.sensors import router as sources_router
from api.routes.live import router as live_router
from api.routes.dashboard import router as dashbord_router


app = FastAPI(
    title="DAQ Platform API",
    version="0.1.0",
)


app.mount(
    "/dashboard-static",
    StaticFiles(directory="dashboard"),
    name="dashboard-static",
)



app.include_router(status_router)
app.include_router(sources_router)
app.include_router(samples_router)
app.include_router(live_router)
app.include_router(dashbord_router)