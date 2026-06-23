
from typing import Iterable, Mapping

import pytest

from project.api_auth import app
from fastapi.testclient import TestClient

from project.lib_auth import verifi_token
from project.schemas_auth import SUserIn, TokenData

import asyncio


from project.database.models import init_db as idb




@pytest.fixture(scope="module", autouse=True)
def init_db():
    asyncio.run(idb())

@pytest.fixture(scope="module")
def client() -> TestClient:  # type: ignore
    return TestClient(app)


# def test_read_main(client: TestClient) -> None:
#     resp = client.get("/")
#     assert resp.status_code == 200
#     assert resp.json() == {"msg": "Hello auth api"}


# def test_init_db(init_db):
#     assert False


# def test_create_item():
#     response = client.post(
#         "/items/",
#         headers={"X-Token": "coneofsilence"},
#         json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
#     )
#     assert response.status_code == 200
#     assert response.json() == {
#         "id": "foobar",
#         "title": "Foo Bar",
#         "description": "The Foo Barters",
#     }


def test_create_user(client: TestClient) -> None:
    user_req = SUserIn(
        username="Dima", email="sibiriakoff2006@yandex.ru", password="password"
    ).model_dump()

    resp = client.post("/api/auth/register/", json=user_req)
    
    assert resp.status_code == 200

    assert resp.json() == {'username': 'Dima', 'full_name': None, 'email': 'sibiriakoff2006@yandex.ru', 'balance': 0.0, 'disabled': False, 'permissions': []}

def test_get_token(client: TestClient ) -> None:
    form_data: Mapping[str, str | Iterable[str]] = {
        "grant_type": "password",
        "scope": ["me", "items", "cart", "orders", "payment"],
        "username": "Dima",
        "password": "password"
        }
    # access_token = create_access_token(form_data["username"], form_data["scope"]) # type: ignore
    resp = client.post("/api/auth/token/", data=form_data)
    token = resp.json()
    token_data: TokenData = verifi_token(token["access_token"])
    
    assert resp.status_code == 200
    assert token_data.username == form_data["username"]

# @pytest.mark.anyio
# async def test_root(init_db):
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         response = await ac.get("/")
#     assert response.status_code == 200
# #     assert resp.json() == {"msg": "Hello auth api"}

#     assert response.json() == {"msg": "Hello auth api"}

# @pytest.mark.skip(reason=None)
# @pytest.mark.anyio
# async def test_create_user():
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         user_req = SUserIn(
#             username="Dima", email="sibiriakoff2007@yandex.ru", password="password"
#         ).model_dump()
#         response = await ac.post("/api/auth/register/", json=user_req)
#     # print(f"os.environ.get('CONFIG_MODE') ------->>>>> {os.environ.get('CONFIG_MODE')}")
#     assert response.status_code == 200
#     assert response.json() == {'username': 'Dima', 'full_name': None, 'email': 'sibiriakoff2007@yandex.ru', 'balance': 0.0, 'disabled': False, 'permissions': []}

