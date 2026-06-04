from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.0-flash", env="GEMINI_MODEL")

    eje_cloud_url: str = Field("https://ejecloud.jusbaires.gob.ar", env="EJE_CLOUD_URL")
    eje_cloud_user: str = Field("", env="EJE_CLOUD_USER")
    eje_cloud_password: str = Field("", env="EJE_CLOUD_PASSWORD")

    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(False, env="DEBUG")

    browser_timeout: int = Field(30000, env="BROWSER_TIMEOUT")
    browser_headless: bool = Field(True, env="BROWSER_HEADLESS")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
