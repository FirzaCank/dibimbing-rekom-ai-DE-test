"""Unit tests for the language normalization, the core logic of Task 1.

Uses an inline fixture (no network) so the tests are deterministic and fast.
The fixture mirrors the brief's worked example: Indonesia (1 language) and
Iraq (3 languages: Arabic, Aramaic, Sorani).
"""

from app.countries import normalize, to_db_rows
from app.db import _COLUMNS

# Minimal subset of the REST Countries API shape we depend on.
FIXTURE = [
    {
        "name": {"common": "Indonesia"},
        "cca3": "IDN",
        "region": "Asia",
        "subregion": "South-Eastern Asia",
        "languages": {"ind": "Indonesian"},
    },
    {
        "name": {"common": "Iraq"},
        "cca3": "IRQ",
        "region": "Asia",
        "subregion": "Western Asia",
        "languages": {"ara": "Arabic", "arc": "Aramaic", "ckb": "Sorani"},
    },
]


def test_iraq_explodes_into_three_rows():
    entries, _, _ = normalize(FIXTURE)
    iraq = [e for e in entries if e.country_name == "Iraq"]
    assert len(iraq) == 3
    assert {(e.lang_code, e.lang_name) for e in iraq} == {
        ("ara", "Arabic"),
        ("arc", "Aramaic"),
        ("ckb", "Sorani"),
    }


def test_indonesia_single_row():
    entries, _, _ = normalize(FIXTURE)
    idn = [e for e in entries if e.country_name == "Indonesia"]
    assert len(idn) == 1
    assert idn[0].cca3 == "IDN"
    assert idn[0].subregion == "South-Eastern Asia"
    assert idn[0].lang_code == "ind"


def test_total_countries_is_country_count_not_row_count():
    entries, _, total = normalize(FIXTURE)
    # 2 countries, but 4 language rows (1 + 3).
    assert total == 2
    assert len(entries) == 4


def test_country_with_no_languages_produces_no_row_but_counts():
    fixture = FIXTURE + [
        {"name": {"common": "Nowhere"}, "cca3": "NWH", "region": "Asia", "subregion": "X"}
    ]
    entries, _, total = normalize(fixture)
    assert total == 3  # Nowhere still counts as a country
    assert all(e.country_name != "Nowhere" for e in entries)  # but no language row


def test_db_rows_follow_column_order_and_store_api_region():
    entries, api_regions, _ = normalize(FIXTURE)
    rows = to_db_rows(entries, api_regions, "p3kw91zrx42mb", "7284015")
    # _COLUMNS = (raw_id, user_id, country_name, cca3, region, subregion, lang_code, lang_name)
    assert len(rows[0]) == len(_COLUMNS)
    raw_id, user_id, country_name, cca3, region, subregion, lang_code, lang_name = rows[0]
    assert raw_id == "p3kw91zrx42mb"
    assert user_id == "7284015"
    assert region == "Asia"  # API per-country value, not the request "asia"
