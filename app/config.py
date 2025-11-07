from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    origins_str: str = "http://localhost,http://localhost:3000" 
    class Config:
        env_file = ".env"
    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.origins_str.split(",")]
settings = Settings()