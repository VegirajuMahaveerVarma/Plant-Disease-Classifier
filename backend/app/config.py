from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = ""
    model_path: str = "models/plant_disease_resnet18.pt"
    class_names_path: str = "models/class_names.json"
    max_upload_mb: int = 8
    cors_origins: str = "http://localhost:3000"

    @property
    def backend_dir(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def resolved_model_path(self) -> Path:
        p = Path(self.model_path)
        return p if p.is_absolute() else self.backend_dir / p

    @property
    def resolved_class_names_path(self) -> Path:
        p = Path(self.class_names_path)
        return p if p.is_absolute() else self.backend_dir / p

    @property
    def allowed_origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
