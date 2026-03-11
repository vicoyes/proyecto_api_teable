from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Task API"
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8002
    app_api_key: str | None = None

    teable_base_url: str
    teable_api_token: str

    teable_table_tasks: str
    teable_table_team: str
    teable_table_projects: str
    teable_table_clientes: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
