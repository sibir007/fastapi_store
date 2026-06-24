from decimal import Decimal
from typing import Iterable, Mapping

from httpx import ASGITransport, AsyncClient
import pytest

from project.api_auth import app
from fastapi.testclient import TestClient

from project.lib_auth import verifi_token
from project.schemas_auth import STopupIn, SUserIn, TokenData

import asyncio


from project.database.models import init_db as idb
import logging

logger = logging.getLogger(__name__)

# @pytest.fixture(autouse=True)
@pytest.fixture(scope="module", autouse=True)
def init_db():
    asyncio.run(idb())


# @pytest.fixture()
@pytest.fixture(scope="module")
def client() -> TestClient:  # type: ignore
    return TestClient(app)



@pytest.mark.skip(reason="None")
def test_create_user(client: TestClient) -> None:
    user_req = SUserIn(
        username="Dima", email="sibiriakoff2006@yandex.ru", password="password"
    ).model_dump()
    resp = client.post("/api/auth/register/", json=user_req)

    assert resp.status_code == 200

    assert resp.json() == {
        "username": "Dima",
        "full_name": None,
        "email": "sibiriakoff2006@yandex.ru",
        "balance": 0.0,
        "disabled": False,
        "permissions": [],
    }


# @pytest.mark.skip(reason="None")
@pytest.mark.anyio
async def test_create_user_async() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        user_req = SUserIn(
            username="Dima", email="sibiriakoff2006@yandex.ru", password="password"
        ).model_dump()
        resp = await ac.post("/api/auth/register/", json=user_req)

        assert resp.status_code == 200

        assert resp.json() == {
            "username": "Dima",
            "full_name": None,
            "email": "sibiriakoff2006@yandex.ru",
            "balance": 0.0,
            "disabled": False,
            "permissions": [],
        }


@pytest.mark.skip(reason="None")
def test_get_token(client: TestClient) -> None:
    form_data: Mapping[str, str | Iterable[str]] = {
        "grant_type": "password",
        "scope": ["me", "items", "cart", "orders", "payment"],
        "username": "Dima",
        "password": "password",
    }
    # access_token = create_access_token(form_data["username"], form_data["scope"]) # type: ignore
    resp = client.post("/api/auth/token/", data=form_data)
    assert resp.status_code == 200

    token = resp.json()
    token_data: TokenData = verifi_token(token["access_token"])

    assert token_data.username == form_data["username"]


# @pytest.mark.skip(reason="None")
@pytest.mark.anyio
async def test_get_token_async() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        form_data: Mapping[str, str | Iterable[str]] = {
            "grant_type": "password",
            "scope": "me items cart orders payment admin_permissions",
            "username": "Dima",
            "password": "password",
        }
        # access_token = create_access_token(form_data["username"], form_data["scope"]) # type: ignore
        resp = await ac.post("/api/auth/token/", data=form_data)
        assert resp.status_code == 200

        token = resp.json()
        token_data: TokenData = verifi_token(token["access_token"])
        # print(f"token_data ----->>>>> {token_data}")
        assert token_data.username == form_data["username"]

@pytest.mark.skip(reason="None")
def test_topup(client: TestClient) -> None:
    topup1_ammount = 15000.0
    topup2_ammount = 10000.0
    topup_data: STopupIn = STopupIn(ammount=Decimal(str(topup1_ammount)))
    topup2_data: STopupIn = STopupIn(ammount=Decimal(str(topup2_ammount)))
    form_data: Mapping[str, str | Iterable[str]] = {
        "grant_type": "password",
        "scope": "me items cart orders payment admin_permissions",
        "username": "Dima",
        "password": "password",
    }

    token_resp = client.post("/api/auth/token/", data=form_data)
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]  # access_token
    # print(f"token ----->>>>> {token}")
    user_profile_resp = client.get(
        "/api/auth/profile/", headers={"Authorization": f"Bearer {token}"}
    )
    assert user_profile_resp.status_code == 200
    assert user_profile_resp.json()["balance"] == 0.0

    topup_resp = client.post(
        "/api/auth/topup/",
        headers={"Authorization": f"Bearer {token}"},
        json=topup_data.model_dump(),
    )

    assert topup_resp.status_code == 200
    assert topup_resp.json()["topup"] == topup1_ammount
    assert topup_resp.json()["balance"] == topup1_ammount

    topup2_resp = client.post(
        "/api/auth/topup/",
        headers={"Authorization": f"Bearer {token}"},
        json=topup2_data.model_dump(),
    )

    assert topup2_resp.status_code == 200
    assert topup2_resp.json()["topup"] == topup2_ammount
    assert topup2_resp.json()["balance"] == topup1_ammount + topup2_ammount


# @pytest.mark.skip(reason="None")
@pytest.mark.anyio
async def test_topup_async() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        topup1_ammount = 15000.0
        topup2_ammount = 10000.0
        topup_data = {"ammount": topup1_ammount}
        topup2_data = {"ammount": topup2_ammount}
        form_data: Mapping[str, str | Iterable[str]] = {
            "grant_type": "password",
            "scope": "me items cart orders payment admin_permissions",
            "username": "Dima",
            "password": "password",
        }

        token_resp = await ac.post("/api/auth/token/", data=form_data)
        assert token_resp.status_code == 200
        token = token_resp.json()["access_token"]
        token_info_rsp = await ac.get(
            "/api/auth/token/", headers={"Authorization": f"Bearer {token}"}
        )
        # print(f"token_info_rsp.json() ----->>>>> {token_info_rsp.json()}")
        assert token_info_rsp.status_code == 200
        
          # access_token
        # print(f"verify_token ----->>>>> {verifi_token(token)}")
        user_profile_resp = await ac.get(
            "/api/auth/profile/", headers={"Authorization": f"Bearer {token}"}
        )

        # print(f"user_profile_resp.json() ----->>>>> {user_profile_resp.json()}")
        # print(f"user_profile_resp.headers() ----->>>>> {user_profile_resp.headers}")
        assert user_profile_resp.status_code == 200
        assert user_profile_resp.json()["balance"] == 0.0

        topup_resp = await ac.post(
            "/api/auth/topup/",
            headers={"Authorization": f"Bearer {token}"},
            json=topup_data,
        )

        assert topup_resp.status_code == 200
        assert topup_resp.json()["topup"] == topup1_ammount
        assert topup_resp.json()["balance"] == topup1_ammount

        topup2_resp = await ac.post(
            "/api/auth/topup/",
            headers={"Authorization": f"Bearer {token}"},
            json=topup2_data,
        )

        assert topup2_resp.status_code == 200
        assert topup2_resp.json()["topup"] == topup2_ammount
        assert topup2_resp.json()["balance"] == topup1_ammount + topup2_ammount

