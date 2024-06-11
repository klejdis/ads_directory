import typed_settings as typed_settings


@typed_settings.settings
class Quart:
    DEBUG: bool
    ENV: str
    TESTING: bool
    JWT_SECRET_KEY: str


@typed_settings.settings
class Database:
    URI: str
    ECHO: bool


@typed_settings.settings
class Settings:
    base_path: str
    quart: Quart
    database: Database


settings = typed_settings.load_settings(
    cls=Settings,
    loaders=[
        typed_settings.FileLoader(
            files=[typed_settings.find("config/config.toml")],
            env_var="CONFIG",
            formats={
                "*.toml": typed_settings.TomlFormat("ads_directory"),
            },
        ),
        typed_settings.EnvLoader(prefix=""),
    ],
)
