from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analytics, categories, categorization, ingestion, transactions

# Schema is managed by Alembic (backend/alembic/), not create_all - run
# `alembic upgrade head` before starting the server. See roadmap.txt
# (2026-07-10) for why: create_all + manual ALTER TABLE had already let the
# real dev DB drift from the model (a missing index) without anyone noticing.

app = FastAPI(title="Finance Tracker API")

app.add_middleware(
    CORSMiddleware,
    # Vite picks the next free port if 5173 is taken, so match any localhost port in dev.
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(ingestion.router)
app.include_router(categorization.router)
app.include_router(categories.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
