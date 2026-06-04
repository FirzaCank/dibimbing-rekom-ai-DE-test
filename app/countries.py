# Fetches countries by region from restcountries.com and normalizes the languages field.
# Each country can have multiple languages, so one country produces N rows (one per language).

import httpx
from fastapi import HTTPException

from app.config import settings
from app.models import LanguageEntry


async def fetch_region(region: str) -> list[dict]:
    url = f"{settings.countries_api_base}/region/{region}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}")

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Region not found: {region}")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Upstream returned {resp.status_code}")
    return resp.json()


def normalize(
    countries: list[dict],
) -> tuple[list[LanguageEntry], list[str | None], int]:
    entries: list[LanguageEntry] = []
    # api_regions is kept separate (not on LanguageEntry) because the response model
    # should not expose region — it echoes the request input instead.
    api_regions: list[str | None] = []
    for country in countries:
        country_name = (country.get("name") or {}).get("common")
        cca3 = country.get("cca3")
        subregion = country.get("subregion")
        api_region = country.get("region")
        for lang_code, lang_name in (country.get("languages") or {}).items():
            entries.append(
                LanguageEntry(
                    country_name=country_name,
                    cca3=cca3,
                    subregion=subregion,
                    lang_code=lang_code,
                    lang_name=lang_name,
                )
            )
            api_regions.append(api_region)
    return entries, api_regions, len(countries)


def to_db_rows(
    entries: list[LanguageEntry],
    api_regions: list[str | None],
    raw_id: str,
    user_id: str,
) -> list[tuple]:
    return [
        (raw_id, user_id, e.country_name, e.cca3, region, e.subregion, e.lang_code, e.lang_name)
        for e, region in zip(entries, api_regions)
    ]
