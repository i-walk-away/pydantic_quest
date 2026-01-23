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


class GithubOAuth(BaseSettings):
    client_id: str | None = Field(default=None, alias="GITHUB_CLIENT_ID")
    client_secret: str | None = Field(default=None, alias="GITHUB_CLIENT_SECRET")
    redirect_uri: str | None = Field(default=None, alias="GITHUB_REDIRECT_URI")
    scope: str = Field(default="read:user user:email", alias="GITHUB_SCOPE")
    allow_signup: bool = Field(default=True, alias="GITHUB_ALLOW_SIGNUP")

    authorize_url: str = Field(
        default="https://github.com/login/oauth/authorize",
        alias="GITHUB_AUTHORIZE_URL",
    )

    token_url: str = Field(
        default="https://github.com/login/oauth/access_token",
        alias="GITHUB_TOKEN_URL",
    )

    user_url: str = Field(
        default="https://api.github.com/user",
        alias="GITHUB_USER_URL",
    )

    emails_url: str = Field(
        default="https://api.github.com/user/emails",
        alias="GITHUB_EMAILS_URL",
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database: Database = Field(default_factory=Database)
    auth: Auth = Field(default_factory=Auth)
    github: GithubOAuth = Field(default_factory=GithubOAuth)
    frontend_url: str = Field(
        default="http://localhost:5173",
        alias="FRONTEND_URL",
    )


settings = Settings()
