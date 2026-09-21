from sqlalchemy.orm import Session

from app.repositories import user_repository


def list_users(db: Session, offset: int, limit: int):
    return user_repository.list_users(db, offset, limit)


def get_user(db: Session, user_id: int):
    return user_repository.get_user(db, user_id)


def create_user(db: Session, name: str):
    return user_repository.create_user(db, name)


def update_user(db: Session, user_id: int, name: str):
    return user_repository.update_user(db, user_id, name)


def delete_user(db: Session, user_id: int):
    return user_repository.delete_user(db, user_id)
