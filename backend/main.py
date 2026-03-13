from fastapi import FastAPI
from api import *

app = FastAPI(title="AI Log Anomaly Explainer")

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    log_router,
    prefix="/log",
    tags={"log"}
)
