import re

from .conftest import VALID_PERSON, csrf_from


def test_home_is_consultation_first_and_has_security_headers(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "빌딩모아관리" in res.text
    assert 'href="/diagnosis">상담 신청</a>' in res.text
    assert "공동구매" not in res.text
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "script-src 'none'" in res.headers["Content-Security-Policy"]


def test_home_links_only_to_pages_that_exist(client):
    links = set(re.findall(r'href="(/[^"#]*)"', client.get("/").text))
    assert {"/diagnosis", "/partners", "/privacy", "/terms"} <= links
    for link in links:
        assert client.get(link).status_code == 200, link


def test_group_buying_pages_are_gone(client):
    for path in ("/rounds", "/rounds/test-1", "/demand", "/admin/demand", "/admin/rounds/new",
                 "/admin/export/demand.csv"):
        assert client.get(path, auth=("admin", "test-admin-pw")).status_code == 404, path


def _diagnosis(client, **fields):
    token = csrf_from(client.get("/diagnosis").text)
    data = {"csrf_token": token, **fields}
    return client.post("/diagnosis", data=data, follow_redirects=False)


def test_consultation_form_asks_for_address(client):
    page = client.get("/diagnosis").text
    assert "<h1>상담 신청</h1>" in page
    assert '<label for="district">건물 주소' in page
    assert "공동구매" not in page


def test_diagnosis_requires_collect_consent(client, repo):
    res = _diagnosis(client, **VALID_PERSON)
    assert res.status_code == 400
    assert "개인정보 수집·이용에 동의해야" in res.text
    assert 'value="김건물"' in res.text  # 입력값이 유지됨
    assert repo.list_leads() == []


def test_diagnosis_success_normalizes_values(client, repo):
    res = _diagnosis(client, **VALID_PERSON, consent_collect="on", monthly_cost="120만",
                     has_elevator="no", concerns=["청소", "소방 점검", "없는항목"])
    assert res.status_code == 303
    assert res.headers["location"] == "/thanks?kind=diagnosis"
    [lead] = repo.list_leads()
    assert lead["phone"] == "010-1234-5678"
    assert lead["district"] == "마포구 망원동 123-4"
    assert lead["monthly_cost"] == 1200000
    assert lead["has_elevator"] == 0
    assert lead["concerns"] == "청소, 소방 점검"
    assert lead["consent_marketing"] == 0
    assert lead["status"] == "신규"


def test_diagnosis_validation_errors(client, repo):
    res = _diagnosis(client, name="", phone="123", district="", building_type="성", consent_collect="on")
    assert res.status_code == 400
    for msg in ("이름을(를) 입력", "전화번호를 확인", "건물 주소을(를) 입력", "건물 유형을(를) 골라"):
        assert msg in res.text
    assert repo.list_leads() == []


def test_post_without_csrf_is_rejected(client, repo):
    client.get("/diagnosis")
    res = client.post("/diagnosis", data={**VALID_PERSON, "consent_collect": "on"})
    assert res.status_code == 403
    assert repo.list_leads() == []


def test_post_with_wrong_csrf_is_rejected(client, repo):
    client.get("/diagnosis")
    res = client.post("/diagnosis", data={**VALID_PERSON, "consent_collect": "on", "csrf_token": "x" * 40})
    assert res.status_code == 403


def test_honeypot_submission_is_dropped(client, repo):
    res = _diagnosis(client, **VALID_PERSON, consent_collect="on", website="http://spam")
    assert res.status_code == 303
    assert repo.list_leads() == []


def test_user_input_is_escaped(client, repo, app):
    app.state.settings  # noqa: B018
    _diagnosis(client, **{**VALID_PERSON, "name": "<script>x</script>"}, consent_collect="on")
    res = client.get("/admin/leads", auth=("admin", "test-admin-pw"))
    assert "<script>x</script>" not in res.text
    assert "&lt;script&gt;" in res.text


def test_thanks_pages(client):
    assert "상담 신청이 접수됐습니다" in client.get("/thanks").text
    assert "업체 등록이 접수됐습니다" in client.get("/thanks?kind=partner").text


def test_static_pages(client):
    for path in ("/privacy", "/terms", "/partners", "/thanks"):
        res = client.get(path)
        assert res.status_code == 200
        assert "공동구매" not in res.text, path
    assert client.get("/healthz").text == "ok"
