"""공동구매 희망 등록, 수요 게시판, 협력 업체 등록, 배포 설정 테스트."""

import csv
import io

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, load_settings
from app.web import create_app

from .conftest import ADMIN_PASSWORD, TEST_DATABASE_URL, _reset_postgres, csrf_from

AUTH = ("admin", ADMIN_PASSWORD)

PERSON = {
    "name": "김건물",
    "phone": "010-1234-5678",
    "building_type": "상가주택",
    "floor_area": "60평",
    "floors": "4",
}


def _post_demand(client, **fields):
    token = csrf_from(client.get("/demand").text)
    return client.post("/demand", data={"csrf_token": token, **fields}, follow_redirects=False)


def test_demand_requires_area_category_and_consent(client, repo):
    res = _post_demand(client, **PERSON)
    assert res.status_code == 400
    for msg in ("동네를 골라 주시거나 적어", "항목을(를) 하나 이상", "개인정보 수집·이용에 동의해야"):
        assert msg in res.text
    assert repo.list_demands() == []


def test_demand_rejects_disallowed_category(client, repo):
    res = _post_demand(client, **PERSON, area_other="마포구 망원동", categories=["건물 종합보험"],
                       consent_collect="on")
    assert res.status_code == 400
    assert repo.list_demands() == []


def test_demand_board_counts_and_hides_personal_info(client, repo):
    for i, cats in enumerate([["청소"], ["청소", "소방 점검"], ["청소"]]):
        res = _post_demand(client, **{**PERSON, "name": f"홍길동{i}", "phone": f"0105555000{i}"},
                           area_other="마포구  망원동", categories=cats, consent_collect="on",
                           current_cost="45만")
        assert res.status_code == 303
        assert res.headers["location"] == "/thanks?kind=demand"

    board = repo.demand_board()
    assert board[0] == {"area": "마포구 망원동", "category": "청소", "count": 3}
    assert {"area": "마포구 망원동", "category": "소방 점검", "count": 1} in board

    home = client.get("/").text
    assert "3채</strong> 모임" in home
    assert "2채 더 모이면 업체 견적" in home  # 기준 5채
    for i in range(3):
        assert f"홍길동{i}" not in home
        assert f"0105555000{i}" not in home


def test_same_phone_and_area_merges_instead_of_inflating(client, repo):
    for cats in (["청소"], ["청소"], ["승강기 유지보수"]):
        _post_demand(client, **PERSON, area_other="마포구 망원동", categories=cats, consent_collect="on")
    [d] = repo.list_demands()
    assert d["categories"] == "청소, 승강기 유지보수"
    counts = {(b["area"], b["category"]): b["count"] for b in repo.demand_board()}
    assert counts == {("마포구 망원동", "청소"): 1, ("마포구 망원동", "승강기 유지보수"): 1}

    # 다른 동네는 따로 셉니다.
    _post_demand(client, **PERSON, area_other="마포구 합정동", categories=["청소"], consent_collect="on")
    assert len(repo.list_demands()) == 2


def test_cancelled_demand_leaves_board(client, repo):
    _post_demand(client, **PERSON, area_other="마포구 망원동", categories=["청소"], consent_collect="on")
    [d] = repo.list_demands()
    repo.update_status("demands", d["id"], "취소", "")
    assert repo.demand_board() == []


def test_board_marks_threshold_reached(tmp_path):
    settings = Settings(admin_password=ADMIN_PASSWORD, demand_threshold=2,
                        database_path=str(tmp_path / "t.db"))
    if TEST_DATABASE_URL:
        _reset_postgres(TEST_DATABASE_URL)
        settings = Settings(admin_password=ADMIN_PASSWORD, demand_threshold=2,
                            database_url=TEST_DATABASE_URL)
    client = TestClient(create_app(settings))
    for i in range(2):
        _post_demand(client, **{**PERSON, "phone": f"0107777000{i}"}, area_other="망원동",
                     categories=["청소"], consent_collect="on")
    assert "기준을 채웠습니다" in client.get("/").text
    admin = client.get("/admin", auth=AUTH).text
    assert "기준 도달" in admin
    assert "/admin/rounds/new?category=%EC%B2%AD%EC%86%8C&amp;area=%EB%A7%9D%EC%9B%90%EB%8F%99" in admin
    prefilled = client.get("/admin/rounds/new?category=청소&area=망원동", auth=AUTH).text
    assert '<option value="청소" selected>' in prefilled
    assert 'value="망원동"' in prefilled


def test_service_dong_select(tmp_path):
    settings = Settings(service_area="마포구", service_dongs=("망원동", "합정동"),
                        database_path=str(tmp_path / "t.db"))
    if TEST_DATABASE_URL:
        _reset_postgres(TEST_DATABASE_URL)
        settings = Settings(service_area="마포구", service_dongs=("망원동", "합정동"),
                            database_url=TEST_DATABASE_URL)
    app = create_app(settings)
    client = TestClient(app)
    page = client.get("/demand").text
    assert '<option value="합정동">' in page
    res = _post_demand(client, **PERSON, dong="합정동", categories=["방역"], consent_collect="on")
    assert res.status_code == 303
    assert app.state.repo.list_demands()[0]["area"] == "마포구 합정동"
    # 목록에 없는 값을 보내면 직접 입력이 없으므로 거부
    res = _post_demand(client, **PERSON, dong="없는동", categories=["방역"], consent_collect="on")
    assert res.status_code == 400


def test_partner_registration_and_admin(client, repo):
    token = csrf_from(client.get("/partners").text)
    base = {"csrf_token": token, "company": "○○클린", "contact_name": "이담당", "phone": "02-123-4567",
            "service_area": "마포구 전체", "categories": ["청소", "방역"], "bulk_discount": "가능"}
    res = client.post("/partners", data={**base, "email": "not-an-email"})
    assert res.status_code == 400
    assert "이메일 주소를 확인" in res.text
    assert "개인정보 수집·이용에 동의해야" in res.text

    res = client.post("/partners", data={**base, "email": "a@b.kr", "consent_collect": "on",
                                         "license_info": "=cmd"}, follow_redirects=False)
    assert res.status_code == 303
    [p] = repo.list_partners()
    assert p["phone"] == "02-123-4567" and p["categories"] == "청소, 방역"

    page = client.get("/admin/partners", auth=AUTH).text
    assert "○○클린" in page
    res = client.post(f"/admin/partners/{p['id']}", data={"status": "견적 받음", "admin_memo": "",
                                                           "csrf_token": token}, auth=AUTH,
                      follow_redirects=False)
    assert res.status_code == 303
    assert repo.get_partner(p["id"])["status"] == "견적 받음"

    export = client.get("/admin/export/partners.csv", auth=AUTH)
    rows = list(csv.reader(io.StringIO(export.text.lstrip("﻿"))))
    assert rows[1][2] == "○○클린" and rows[1][8] == "'=cmd"


def test_admin_demand_page_and_csv(client, repo):
    _post_demand(client, **PERSON, area_other="마포구 망원동", categories=["청소"], consent_collect="on")
    [d] = repo.list_demands()
    assert client.get("/admin/demand").status_code == 401
    page = client.get("/admin/demand", auth=AUTH)
    assert "김건물" in page.text
    assert page.headers["X-Robots-Tag"] == "noindex, nofollow"
    token = csrf_from(page.text)
    res = client.post(f"/admin/demand/{d['id']}", data={"status": "연락함", "admin_memo": "수요일 통화",
                                                         "csrf_token": token}, auth=AUTH,
                      follow_redirects=False)
    assert res.status_code == 303
    export = client.get("/admin/export/demand.csv", auth=AUTH)
    rows = list(csv.reader(io.StringIO(export.text.lstrip("﻿"))))
    assert rows[1][4] == "마포구 망원동" and rows[1][12] == "연락함"


def test_update_status_rejects_unknown_table_or_status(repo):
    with pytest.raises(ValueError):
        repo.update_status("rounds; DROP TABLE leads", 1, "신규", "")
    with pytest.raises(ValueError):
        repo.update_status("leads", 1, "없는상태", "")


def test_vercel_requires_database_url(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        load_settings()
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host:6543/postgres")
    assert load_settings().database_url.endswith("/postgres")


def test_env_settings_parsing(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("SERVICE_DONGS", " 망원동, 합정동 ,,")
    monkeypatch.setenv("DEMAND_THRESHOLD", "abc")
    s = load_settings()
    assert s.service_dongs == ("망원동", "합정동")
    assert s.demand_threshold == 5
    assert s.brand_name == "빌딩모아관리"
