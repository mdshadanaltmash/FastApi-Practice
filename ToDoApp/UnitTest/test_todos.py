from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app
from routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
import pytest
from models import Todos

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


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

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


def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == [{'id': 1,
                                'title': 'Learn to Code!',
                                'description': 'Need to learn everyday!',
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == 200
    assert response.json() == {'id': 1,
                               'title': 'Learn to Code!',
                               'description': 'Need to learn everyday!',
                               'priority': 5,
                               'complete': False,
                               'owner_id': 1}


def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': "todo_id 999, not found."}


def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo!',
        'description': 'New todo description',
        'priority': 5,
        'complete': False
    }
    resp = client.post('/todo/', json=request_data)
    assert resp.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(test_todo):
    request_data = {
        'title': 'Update Todo!',
        'description': 'Update todo description',
        'priority': 4,
        'complete': False
    }
    resp = client.put('/todo/1', json=request_data)
    assert resp.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Update Todo!',
        'description': 'Update todo description',
        'priority': 4,
        'complete': False
    }
    resp = client.put('/todo/999', json=request_data)
    assert resp.status_code == 404
    assert resp.json() == {'detail': "todo_id 999, not found."}


def test_delete_todo(test_todo):
    resp = client.delete('/todo/1')
    assert resp.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    resp = client.delete('/todo/999')
    assert resp.status_code == 404
    assert resp.json() == {'detail': "todo_id 999, not found."}
