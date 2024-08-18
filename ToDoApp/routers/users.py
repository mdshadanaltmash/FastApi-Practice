from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from passlib.handlers.bcrypt import bcrypt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT

from database import SessionLocal
from models import Users
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/', status_code=HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail='Not Authenticated')

    user_info = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_info:
        raise HTTPException(status_code=404, detail='User not found!')

    return user_info


@router.put('/change_password', status_code=HTTP_202_ACCEPTED)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if not user:
        raise HTTPException(status_code=401, detail='Not Authenticated')

    user_info = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt.verify(user_verification.password, user_info.hashed_password):
        raise HTTPException(status_code=401, detail='Old password is incorrect')

    user_info.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_info)
    db.commit()


@router.put('/phone_number/{phone_number}', status_code=HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if not user:
        raise HTTPException(status_code=401, detail='Not Authenticated')

    user_info = db.query(Users).filter(Users.id == user.get('id')).first()
    user_info.phone_number = phone_number

    db.add(user_info)
    db.commit()
