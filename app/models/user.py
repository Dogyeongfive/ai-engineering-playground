from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
