from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED, HTTP_401_UNAUTHORIZED

from UnitTest.utils import *
from routers.users import get_current_user, get_db


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    resp = client.get('/user')

    assert resp.status_code == HTTP_200_OK
    assert resp.json()['username'] == 'mdshadan'
    assert resp.json()['email'] == 'mdshadan@gmail.com'
    assert resp.json()['first_name'] == 'Md Shadan'
    assert resp.json()['last_name'] == 'Altmash'
    assert resp.json()['role'] == 'admin'
    assert resp.json()['phone_number'] == '111-222-333'


def test_change_password_success(test_user):
    resp = client.put('/user/change_password', json={"password": "test123", "new_password": "test1234"})

    assert resp.status_code == HTTP_202_ACCEPTED


def test_change_password_invalid(test_user):
    resp = client.put('/user/change_password', json={"password": "test1234", "new_password": "test1234"})

    assert resp.status_code == HTTP_401_UNAUTHORIZED
    assert resp.json() == {"detail": "Old password is incorrect"}


def test_change_phone_number_success(test_user):
    resp = client.put('/user/phone_number/123456789')

    assert resp.status_code == HTTP_204_NO_CONTENT
