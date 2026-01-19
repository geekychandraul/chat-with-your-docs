from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db.database import async_get_db, local_session
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService

logger = get_logger(__name__)

router = APIRouter(tags=["auth"])
manager = LoginManager(settings.SECRET_KEY.get_secret_value(), token_url="/login")


@manager.user_loader()
async def load_user(username: str) -> User | None:
    async with local_session() as db:
        user_service = UserService(db)
        user = await user_service.get_user_profile(username)
        return user


@router.post("/register")
async def register(
    data: UserCreate,
    db: Session = Depends(async_get_db),
):
    user_service = UserService(db)
    logger.info(f"Registering user: {data.username}")
    new_user = await user_service.register_user(
        name=data.name,
        username=data.username,
        email=data.email,
        password=data.password,
    )
    return {"msg": "User registered successfully", "user": new_user}


@router.post("/login")
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(async_get_db),
) -> dict:
    username = data.username
    password = data.password
    logger.info(f"User login attempt: {username}")

    user = await UserService(db).authenticate_user(username, password)
    logger.info(
        f"Authentication result for user {username}: {'Success' if user else 'Failure'}"
    )
    if not user:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(data={"sub": username})
    return {"access_token": access_token}
