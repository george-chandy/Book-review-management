from pydantic_settings import BaseSettings, SettingsConfigDict


class BookReviewBaseSetting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(BookReviewBaseSetting):
    DATABASE_URL: str


config = Config()
