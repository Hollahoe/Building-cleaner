"""협력 업체 등록, 상태 변경 보호, 배포 설정 테스트."""

import csv
import io

import pytest

from app.config import load_settings

from .conftest import ADMIN_PASSWORD, csrf_from

AUTH = ("admin", ADMIN_PASSWORD)


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


def test_partner_rejects_disallowed_category(client, repo):
    token = csrf_from(client.get("/partners").text)
    res = client.post("/partners", data={
        "csrf_token": token, "company": "○○보험", "contact_name": "이담당", "phone": "02-123-4567",
        "service_area": "마포구", "categories": ["건물 종합보험"], "bulk_discount": "가능",
        "consent_collect": "on",
    })
    assert res.status_code == 400
    assert repo.list_partners() == []


def test_update_status_rejects_unknown_table_or_status(repo):
    with pytest.raises(ValueError):
        repo.update_status("rounds; DROP TABLE leads", 1, "신규", "")
    with pytest.raises(ValueError):
        repo.update_status("demands", 1, "대기", "")
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
    monkeypatch.delenv("FEE_TEXT", raising=False)
    monkeypatch.setenv("SERVICE_AREA", "서대문구")
    s = load_settings()
    assert s.service_area == "서대문구"
    assert s.brand_name == "빌딩모아관리"
    assert "월 요금" in s.fee_text
