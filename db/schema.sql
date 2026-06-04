-- Task 1 PostgreSQL table schema (per the technical test brief).
-- One row per (country, language) pair after normalizing the languages dict.

CREATE TABLE IF NOT EXISTS country_languages (
    id            SERIAL PRIMARY KEY,
    raw_id        VARCHAR(13),
    user_id       VARCHAR(7),
    country_name  TEXT,
    cca3          VARCHAR(3),
    region        TEXT,
    subregion     TEXT,
    lang_code     VARCHAR(10),
    lang_name     TEXT
);
