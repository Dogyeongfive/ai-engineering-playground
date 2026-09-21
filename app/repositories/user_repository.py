from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def list_users(db: Session, offset: int, limit: int):
    statement = (
        select(User)
        .order_by(User.user_id)
        .offset(offset)
        .limit(limit)
    )
    return db.scalars(statement).all()


def get_user(db: Session, user_id: int):
    return db.get(User, user_id)


def create_user(db: Session, name: str):
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, name: str):
    user = get_user(db, user_id)
    if user is None:
        return None

    user.name = name
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True
