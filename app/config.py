from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rekom:rekom@localhost:5432/rekom"
    countries_api_base: str = "https://restcountries.com/v3.1"


settings = Settings()
