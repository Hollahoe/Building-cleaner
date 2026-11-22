import os
import re

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.web import create_app

ADMIN_PASSWORD = "test-admin-pw"


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "")
ALL_TABLES = ("leads", "partners")


def _reset_postgres(url: str) -> None:
    import psycopg

    with psycopg.connect(url) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {', '.join(ALL_TABLES)} CASCADE")


@pytest.fixture
def settings(tmp_path):
    """기본은 임시 SQLite. TEST_DATABASE_URL이 있으면 그 Postgres를 비우고 씁니다."""
    if TEST_DATABASE_URL:
        _reset_postgres(TEST_DATABASE_URL)
        return Settings(admin_password=ADMIN_PASSWORD, database_url=TEST_DATABASE_URL)
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


VALID_PERSON = {
    "name": "김건물",
    "phone": "01012345678",
    "district": "마포구 망원동 123-4",
    "building_type": "상가주택",
    "floor_area": "60평",
    "floors": "4",
}
