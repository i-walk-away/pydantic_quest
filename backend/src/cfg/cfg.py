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


class ExecutionSettings(BaseSettings):
    piston_url: str = Field(default="http://piston:2000", alias="PISTON_URL")
    language: str = Field(default="python", alias="PISTON_LANGUAGE")
    version: str = Field(default="3.12", alias="PISTON_VERSION")
    run_timeout_ms: int = Field(default=10000, alias="PISTON_RUN_TIMEOUT_MS")
    compile_timeout_ms: int = Field(default=10000, alias="PISTON_COMPILE_TIMEOUT_MS")
    run_memory_limit_bytes: int = Field(default=134_217_728, alias="PISTON_RUN_MEMORY_LIMIT_BYTES")
    compile_memory_limit_bytes: int = Field(default=134_217_728, alias="PISTON_COMPILE_MEMORY_LIMIT_BYTES")
    max_output_chars: int = Field(default=16000, alias="EXECUTION_MAX_OUTPUT_CHARS")
    max_user_code_chars: int = Field(default=20000, alias="EXECUTION_MAX_USER_CODE_CHARS")
    max_eval_script_chars: int = Field(default=60000, alias="EXECUTION_MAX_EVAL_SCRIPT_CHARS")
    max_source_chars: int = Field(default=80000, alias="EXECUTION_MAX_SOURCE_CHARS")
    max_retries: int = Field(default=2, alias="PISTON_MAX_RETRIES")
    retry_delay_ms: int = Field(default=200, alias="PISTON_RETRY_DELAY_MS")
    health_check_ttl_sec: int = Field(default=30, alias="PISTON_HEALTH_TTL_SEC")
    http_timeout_ms: int = Field(default=5000, alias="PISTON_HTTP_TIMEOUT_MS")
    rate_limit_window_sec: int = Field(default=60, alias="EXECUTION_RATE_LIMIT_WINDOW_SEC")
    rate_limit_max: int = Field(default=20, alias="EXECUTION_RATE_LIMIT_MAX")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database: Database = Field(default_factory=Database)
    auth: Auth = Field(default_factory=Auth)
    github: GithubOAuth = Field(default_factory=GithubOAuth)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    frontend_url: str = Field(
        default="http://localhost:5173",
        alias="FRONTEND_URL",
    )


settings = Settings()
