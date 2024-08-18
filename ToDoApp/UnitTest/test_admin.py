from UnitTest.utils import *
from routers.admin import get_db, get_current_user
from starlette import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    resp = client.get("/admin/todo")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [{'title': 'Learn to Code!', 'owner_id': 1, 'priority': 5, 'complete': False, 'id': 1,
                           'description': 'Need to learn everyday!'}]


def test_admin_delete_todo(test_todo):
    resp = client.delete("/admin/todo/1")

    assert resp.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_not_found(test_todo):
    resp = client.delete("admin/todo/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {'detail': 'Todo id 9999, not found!'}
