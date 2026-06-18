from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    output_dir: str = "output"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()