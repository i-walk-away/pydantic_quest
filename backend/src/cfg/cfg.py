from dotenv import find_dotenv, load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv(".env"))


class Database(BaseSettings):
    host: str = Field(alias="DB_HOST")
    port: int = Field(alias="DB_PORT")

    database: str = Field(alias="DB_NAME")
    username: str = Field(alias="DB_USERNAME")
    password: str = Field(alias="DB_PASSWORD")

    @computed_field
    @property
    def url(self) -> str:
        return f"mysql+aiomysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class Auth(BaseSettings):
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(alias='JWT_ALGORITHM')
    jwt_lifespan: int = Field(alias='JWT_LIFESPAN')  # in minutes


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database: Database = Field(default_factory=Database)
    auth: Auth = Field(default_factory=Auth)


settings = Settings()
