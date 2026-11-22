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
    assert "공동구매" not in res.text


def test_admin_post_requires_csrf(client, repo):
    lead_id = repo.add_lead({"name": "김", "phone": "010-1234-5678", "district": "마포구",
                             "building_type": "상가주택"})
    client.get("/admin", auth=AUTH)
    res = client.post(f"/admin/leads/{lead_id}", data={"status": "연락함"}, auth=AUTH)
    assert res.status_code == 403
    assert repo.get_lead(lead_id)["status"] == "신규"


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
    assert rows[0][4] == "건물 주소"
    assert rows[1][2].startswith("'=")  # 엑셀 수식 실행 방지
    assert rows[1][13] == "연락함"
