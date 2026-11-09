import re
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.db import today_kst
from app.main import create_app
from app.rounds import parse_tiers, tiers_to_json

ADMIN_PASSWORD = "test-admin-pw"


@pytest.fixture
def settings(tmp_path):
    return Settings(admin_password=ADMIN_PASSWORD, database_path=str(tmp_path / "test.db"))


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def repo(app):
    return app.state.repo


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "폼에 CSRF 토큰이 없습니다"
    return match.group(1)


def round_data(**overrides):
    data = {
        "title": "망원동 청소 공동구매",
        "category": "청소",
        "district": "마포구 망원동",
        "summary": "주 2회 계단 청소",
        "details": "",
        "target_buildings": 10,
        "deadline": (today_kst() + timedelta(days=10)).isoformat(),
        "status": "open",
        "tiers_json": tiers_to_json(parse_tiers("1=450000\n3=420000\n5=400000\n10=380000")),
        "price_note": "예상 단가입니다.",
        "fee_disclosure": "업체 대가 없음",
    }
    data.update(overrides)
    return data


@pytest.fixture
def make_round(repo):
    counter = {"n": 0}

    def _make(**overrides):
        counter["n"] += 1
        slug = f"test-{counter['n']}"
        repo.add_round(round_data(**overrides), slug)
        return slug

    return _make


VALID_PERSON = {
    "name": "김건물",
    "phone": "01012345678",
    "district": "마포구 망원동",
    "building_type": "상가주택",
    "floor_area": "60평",
    "floors": "4",
}
