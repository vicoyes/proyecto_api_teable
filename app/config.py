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
    teable_table_correos: str | None = None  # Opcional: si no se define, endpoints de correos devuelven 503
    teable_table_tickets: str = "tblF4h8mUQKVNmUR9a8"

    # Tabla tareas: enlace a proyecto. Nombre de columna en Teable (fieldKeyType=name).
    teable_field_tasks_proyecto: str = "Proyecto"
    # Field ID estable en Teable (mismo campo). Si se define, el enlace se escribe con PATCH usando fieldKeyType=id.
    teable_field_tasks_proyecto_fld: str | None = "fld83VUmoLSxNf7NHjC"

    auth_username: str = "admin"
    auth_password: str = "admin"
    auth_secret_key: str = "change-me-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
