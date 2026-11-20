"""Aplicación FastAPI. Ejecuta: .venv/bin/uvicorn backend.main:app --reload"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend import config
from backend.filters_service import router as filters_router
from backend.recommend_service import build_recommendation
from backend.sample_play_service import router as sample_play_router
from backend.situation import SituationError, parse_situation
from backend.store import PlaysStore, require_store, store

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("backend.main")

DEV_ORIGIN = "http://localhost:5173"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Carga única y síncrona antes de aceptar peticiones. Nunca termina el proceso.
    store.load()
    if store.error:
        log.error(store.error)
    yield


app = FastAPI(title="Hackathon NFL UNAM", lifespan=lifespan)

if os.environ.get("APP_ENV") == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[DEV_ORIGIN],
        allow_methods=["GET"],
        allow_headers=["*"],
    )


@app.exception_handler(SituationError)
async def situation_error_handler(_: Request, exc: SituationError) -> JSONResponse:
    return exc.to_response()


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("Error no controlado: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Inténtalo de nuevo."},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


api_router = APIRouter(prefix="/api")
api_router.include_router(filters_router)
api_router.include_router(sample_play_router)


@api_router.get("/recommend")
def get_recommend(request: Request, st: PlaysStore = Depends(require_store)) -> dict:
    f = parse_situation(dict(request.query_params), st)
    return build_recommendation(st.df, f)


app.include_router(api_router)

# El montaje estático va al final para que /health y /api/* tengan prioridad.
if config.DIST_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(config.DIST_DIR), html=True), name="static")
