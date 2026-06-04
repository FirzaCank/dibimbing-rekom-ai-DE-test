import asyncpg

from app.config import settings

_pool: asyncpg.Pool | None = None

# must match copy_records_to_table columns and the tuple order in to_db_rows
_COLUMNS = (
    "raw_id",
    "user_id",
    "country_name",
    "cca3",
    "region",
    "subregion",
    "lang_code",
    "lang_name",
)


async def init_pool() -> None:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=10)


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return _pool


async def insert_language_rows(rows: list[tuple]) -> int:
    if not rows:
        return 0
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.copy_records_to_table(
            "country_languages",
            records=rows,
            columns=_COLUMNS,
        )
    return len(rows)
