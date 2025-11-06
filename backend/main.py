"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI

from .api.routes import models as model_routes
from .database import engine
from .models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bambu Clone API")
app.include_router(model_routes.router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint."""

    return {"status": "ok"}
