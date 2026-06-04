from pydantic import BaseModel, Field


class CountryRequest(BaseModel):
    raw_id: str = Field(
        ...,
        min_length=13,
        max_length=13,
        pattern=r"^[A-Za-z0-9]{13}$",
        examples=["p3kw91zrx42mb"],
    )
    user_id: str = Field(
        ...,
        pattern=r"^\d{7}$",
        examples=["7284015"],
    )
    region: str = Field(..., min_length=1, examples=["asia"])


class LanguageEntry(BaseModel):
    country_name: str
    cca3: str | None = None
    subregion: str | None = None
    lang_code: str
    lang_name: str


class CountryResponse(BaseModel):
    raw_id: str
    user_id: str
    region: str
    total_countries: int
    returned_entries: list[LanguageEntry]
