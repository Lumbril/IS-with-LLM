from fastapi import FastAPI
from api import auth_router

app = FastAPI(title="AI Log Anomaly Explainer")

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)
