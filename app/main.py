from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import countries, db
from app.models import CountryRequest, CountryResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    yield
    await db.close_pool()


app = FastAPI(title="Rekom Country Languages API", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/countries", response_model=CountryResponse)
async def ingest_countries(payload: CountryRequest) -> CountryResponse:
    raw = await countries.fetch_region(payload.region)
    entries, api_regions, total_countries = countries.normalize(raw)

    rows = countries.to_db_rows(entries, api_regions, payload.raw_id, payload.user_id)
    await db.insert_language_rows(rows)

    return CountryResponse(
        raw_id=payload.raw_id,
        user_id=payload.user_id,
        region=payload.region,
        total_countries=total_countries,
        returned_entries=entries,
    )
