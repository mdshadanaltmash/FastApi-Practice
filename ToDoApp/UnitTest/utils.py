from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from models import Todos, Users
from routers.auth import bcrypt_context

from fastapi.testclient import TestClient
import pytest

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(url=SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'mdshadan', 'id': 1, 'user_role': 'admin'}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='Learn to Code!',
        description='Need to learn everyday!',
        priority=5,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text('Delete from todos;'))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username='mdshadan',
        email='mdshadan@gmail.com',
        first_name='Md Shadan',
        last_name='Altmash',
        hashed_password=bcrypt_context.hash('test123'),
        role='admin',
        phone_number='111-222-333'
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('Delete from Users;'))
        connection.commit()
