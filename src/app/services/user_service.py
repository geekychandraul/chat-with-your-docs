from fastapi.exceptions import HTTPException

from app.core.logging import get_logger
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_repo import UserRepository
from app.utils.crypt import hash_password, verify_password

logger = get_logger(__name__)


class UserService:
    """Service responsible for user-related operations.

    Responsibilities:
      - user registration
      - user authentication
      - user profile management
    """

    def __init__(self, db):
        """Initialize repositories and services.

        Args:
            db: a database session/connection used by repositories.
        """
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditRepository(db)

    async def register_user(
        self,
        name: str,
        username: str,
        email: str,
        password: str,
    ):
        """Register a new user.

        Args:
            username: The username of the user.
            password: The password of the user.

        Raises:
            HTTPException: If the user already exists.
        """
        existing_user = await self.users.get_user(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        hashed_password = hash_password(password)
        new_user = User(
            name=name, username=username, email=email, hashed_password=hashed_password
        )
        await self.users.create_user(new_user)
        await self.audit.log(
            "NEW_USER_REGISTRATION",
            {"username": new_user.username},
            user_id=new_user.uuid,
        )
        return new_user

    async def authenticate_user(self, username: str, password: str) -> User | None:
        user = await self.users.get_user(username)
        # TODO Can be redirected to registration if the user does not exist.
        if user and verify_password(password, user.hashed_password):
            print(user)
            return user
        return None

    async def get_user_profile(self, username: str) -> User | None:
        user = await self.users.get_user(username)
        if user:
            return user
        return None
