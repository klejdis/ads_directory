import logging

from flask_bcrypt import Bcrypt
from pydantic import ValidationError
from quart import Quart
from quart.typing import ResponseReturnValue
from quart_jwt_extended import JWTManager
from quart_schema import Info, QuartSchema, RequestSchemaValidationError, ResponseSchemaValidationError
from werkzeug.exceptions import HTTPException

from ads_directory.blueprints.category import bp as category_bp
from ads_directory.blueprints.custom_fields import bp as custom_fields_bp
from ads_directory.blueprints.listing import bp as listing_bp
from ads_directory.commands.seed import seed_data
from ads_directory.config import settings
from ads_directory.routes import bp

logger = logging.getLogger(__name__)


def create_app() -> Quart:
    app = Quart(__name__)
    # load the settings from the config file
    app.config.from_object(settings.quart)
    # this will prefix all routes with the base path
    app.register_blueprint(bp, url_prefix=f"{settings.base_path}")
    app.register_blueprint(category_bp, url_prefix=f"{settings.base_path}/categories")
    app.register_blueprint(custom_fields_bp, url_prefix=f"{settings.base_path}/custom-fields")
    app.register_blueprint(listing_bp, url_prefix=f"{settings.base_path}/listings")

    Bcrypt(app)
    JWTManager(app)

    QuartSchema(
        app,
        info=Info(title="Ads Directory", version="0.0.1"),
        openapi_path=f"{settings.base_path}/openapi.json",
        swagger_ui_path=f"{settings.base_path}/docs",
        redoc_ui_path=f"{settings.base_path}/redocs",
        tags=[],
        # security_schemes={"Bearer": {"type": "http", "scheme": "bearer"}}, # TODO: add security scheme
        security=[{"Bearer": []}],
    )

    @app.errorhandler(RequestSchemaValidationError)  # type: ignore
    async def handle_request_validation_error(e: RequestSchemaValidationError) -> ResponseReturnValue:
        logger.info("Validation error for request", exc_info=e)
        if isinstance(e.validation_error, ValidationError):
            return {"error": e.validation_error.errors()}, 400
        else:
            return {"error": str(e.validation_error)}, 400

    @app.errorhandler(ResponseSchemaValidationError)  # type: ignore
    async def handle_response_validation_error(e: ResponseSchemaValidationError) -> ResponseReturnValue:
        logger.info("Validation error for response", exc_info=e)
        if isinstance(e.validation_error, ValidationError):
            return {"error": e.validation_error.errors()}, 500
        else:
            return {"error": str(e.validation_error)}, 500

    @app.errorhandler(HTTPException)  # type: ignore
    async def jsonify_http_exceptions(e: HTTPException) -> ResponseReturnValue:
        logger.info(f"An http exception was raised: {str(e)}.", exc_info=e)
        status_code = e.code or 500
        message = e.description or "Unknown error"
        return {"error": message}, status_code

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with dummy data."""
        seed_data()
        print("Database seeded with dummy data.")

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8080)
