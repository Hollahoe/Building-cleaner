import csv
import io

from fastapi.testclient import TestClient

from app.config import Settings
from app.web import create_app

from .conftest import ADMIN_PASSWORD, csrf_from

AUTH = ("admin", ADMIN_PASSWORD)


def test_admin_locked_when_no_password(tmp_path):
    client = TestClient(create_app(Settings(database_path=str(tmp_path / "x.db"))))
    res = client.get("/admin", auth=("admin", ""))
    assert res.status_code == 503


def test_admin_requires_correct_password(client):
    assert client.get("/admin").status_code == 401
    assert client.get("/admin", auth=("admin", "wrong")).status_code == 401
    assert client.get("/admin", auth=("root", ADMIN_PASSWORD)).status_code == 401
    res = client.get("/admin", auth=AUTH)
    assert res.status_code == 200
    assert 'name="robots" content="noindex' in res.text


ROUND_FORM = {
    "title": "망원동 청소 1차",
    "category": "청소",
    "district": "마포구 망원동",
    "summary": "주 2회",
    "target_buildings": "10",
    "deadline": "2099-12-31",
    "status": "open",
    "tiers": "1=450000\n3=420000\n10=380000",
    "price_note": "예상 단가",
    "fee_disclosure": "업체 대가 없음",
}


def test_create_and_edit_round(client, repo):
    token = csrf_from(client.get("/admin/rounds/new", auth=AUTH).text)
    res = client.post("/admin/rounds", data={**ROUND_FORM, "csrf_token": token}, auth=AUTH,
                      follow_redirects=False)
    assert res.status_code == 303
    rid = int(res.headers["location"].rsplit("/", 1)[1])
    row = repo.get_round(rid)
    assert row["title"] == "망원동 청소 1차"
    assert client.get(f"/rounds/{row['slug']}").status_code == 200

    edit = client.get(f"/admin/rounds/{rid}", auth=AUTH)
    assert "1=450000\n3=420000\n10=380000" in edit.text
    res = client.post(f"/admin/rounds/{rid}", data={**ROUND_FORM, "status": "draft",
                                                    "csrf_token": token}, auth=AUTH,
                      follow_redirects=False)
    assert res.status_code == 303
    assert repo.get_round(rid)["status"] == "draft"
    assert client.get(f"/rounds/{row['slug']}").status_code == 404


def test_round_form_rejects_banned_category_and_bad_tiers(client, repo):
    token = csrf_from(client.get("/admin/rounds/new", auth=AUTH).text)
    res = client.post("/admin/rounds", data={**ROUND_FORM, "category": "건물 종합보험",
                                             "tiers": "3=100", "csrf_token": token}, auth=AUTH)
    assert res.status_code == 400
    assert "항목을(를) 골라" in res.text
    assert "첫 구간은 1채" in res.text
    assert repo.list_rounds() == []


def test_admin_post_requires_csrf(client, repo):
    client.get("/admin", auth=AUTH)
    res = client.post("/admin/rounds", data=ROUND_FORM, auth=AUTH)
    assert res.status_code == 403


def test_lead_status_update_and_csv_export(client, repo):
    lead_id = repo.add_lead({"name": "=HYPERLINK(\"x\")", "phone": "010-1234-5678",
                             "district": "마포구", "building_type": "상가주택",
                             "monthly_cost": 1200000, "consent_marketing": 1})
    token = csrf_from(client.get("/admin/leads", auth=AUTH).text)
    res = client.post(f"/admin/leads/{lead_id}", data={"status": "연락함", "admin_memo": "화요일 방문",
                                                        "csrf_token": token}, auth=AUTH,
                      follow_redirects=False)
    assert res.status_code == 303
    assert repo.get_lead(lead_id)["status"] == "연락함"

    bad = client.post(f"/admin/leads/{lead_id}", data={"status": "없는상태", "csrf_token": token},
                      auth=AUTH)
    assert bad.status_code == 400

    export = client.get("/admin/export/leads.csv", auth=AUTH)
    assert export.status_code == 200
    assert export.text.startswith("﻿")
    rows = list(csv.reader(io.StringIO(export.text.lstrip("﻿"))))
    assert rows[0][2] == "이름"
    assert rows[1][2].startswith("'=")  # 엑셀 수식 실행 방지
    assert rows[1][13] == "연락함"


def test_participant_update_and_export(client, repo):
    from .conftest import round_data
    rid = repo.add_round(round_data(), "r1")
    pid = repo.add_participation(rid, {"name": "박", "phone": "010-1111-2222", "district": "망원동",
                                       "building_type": "원룸·다가구", "consent_vendor_share": 1})
    token = csrf_from(client.get(f"/admin/rounds/{rid}", auth=AUTH).text)
    res = client.post(f"/admin/participations/{pid}", data={"status": "확정", "admin_memo": "",
                                                             "csrf_token": token}, auth=AUTH,
                      follow_redirects=False)
    assert res.status_code == 303
    assert repo.get_participation(pid)["status"] == "확정"
    export = client.get(f"/admin/export/rounds/{rid}/participants.csv", auth=AUTH)
    rows = list(csv.reader(io.StringIO(export.text.lstrip("﻿"))))
    assert rows[1][9] == "예" and rows[1][12] == "확정"
    assert client.get("/admin/export/rounds/999/participants.csv", auth=AUTH).status_code == 404
