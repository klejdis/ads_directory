from typing import Any

from flask_bcrypt import check_password_hash, generate_password_hash
from pydantic.fields import Field
from pydantic.main import BaseModel
from quart import Blueprint
from quart_jwt_extended import create_access_token
from quart_schema import validate_request, validate_response
from werkzeug.exceptions import UnprocessableEntity

from ads_directory.config import settings
from ads_directory.dao.base_dao import BaseDao
from ads_directory.models.models import User

bp = Blueprint("", __name__)


class CreatedResponse(BaseModel):
    success: bool
    id: Any | None = None


class DeletedResponse(BaseModel):
    success: bool
    rowcount: int


class ErrorResponse(BaseModel):
    success: bool
    message: str


class PaginatedRequest(BaseModel):
    page: int = 1
    per_page: int = 20


@bp.route("/health")
async def hello() -> str:
    return "Healthy as a horse!"


class LoginRequest(BaseModel):
    email: str = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")


class LoggedInResponse(BaseModel):
    success: bool
    access_token: str


@bp.route("/login", methods=["POST"])
@validate_request(LoginRequest)
@validate_response(LoggedInResponse)
async def login(data: LoginRequest):
    # search for email in database
    # if user is found, check password
    user: User | None = await BaseDao.get_one(User, User.email == data.email)
    if not user:
        return ErrorResponse(success=False, message="User not found")

    # hash the password and compare
    if user and check_password_hash(user.password, data.password):
        access_token = create_access_token(identity=user.id)
        return LoggedInResponse(success=True, access_token=access_token)

    return ErrorResponse(success=False, message="Invalid credentials")


class RegisterUserRequest(BaseModel):
    email: str = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")
    name: str = Field(..., description="The name of the user")
    last_name: str = Field(..., description="The last name of the user")


@bp.post("/register")
@validate_request(RegisterUserRequest)
@validate_response(CreatedResponse)
async def register(data: RegisterUserRequest):
    user: User | None = await BaseDao.get_one(User, User.email == data.email)
    if user:
        raise UnprocessableEntity("User already exists")
    try:
        # substitute the password with a hashed version
        data.password = generate_password_hash(data.password).decode("utf-8")
        # create the user
        user = await BaseDao.create(User, **data.dict())
        return CreatedResponse(success=True, id=user.id)
    except Exception as e:
        raise UnprocessableEntity(str(e))
