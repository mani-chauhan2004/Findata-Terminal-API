from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Literal
from pydantic import AnyUrl, BeforeValidator, computed_field

from app.core.paths import PROJECT_ROOT

_env_file = PROJECT_ROOT / ".env"

def parse_cors(v: any) -> list[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.split for i in v.split(",") if i.split()]
    elif isinstance(v, str | list):
        return v
    else: 
        raise ValueError("[CORS] Invalid CORS configuration, accepts only list of urls or string")

class settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = str(_env_file),
        env_file_encoding = "utf-8",
        case_sensitive = True,
        env_prefix = "TERMINAL_",
        env_prefix_target = "variable",
        nested_model_default_partial_update = False,
    )

    API_V1_STR: str = "api/v1"
    FRONTEND_HOSTS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip('/') for origin in self.BACKEND_CORS_ORIGINS] + self.FRONTEND_HOSTS


    PROJECT_NAME: str


settings = settings()
    


