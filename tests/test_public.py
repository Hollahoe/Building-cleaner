from datetime import timedelta

from app.db import today_kst

from .conftest import VALID_PERSON, csrf_from


def test_home_empty_state_and_security_headers(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "아직 모인 신청이 없습니다" in res.text
    assert "빌딩모아관리" in res.text
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "script-src 'none'" in res.headers["Content-Security-Policy"]


def test_home_lists_open_rounds_only(client, make_round):
    make_round(title="모집 중인 라운드")
    make_round(title="준비 중 라운드", status="draft")
    res = client.get("/")
    assert "모집 중인 라운드" in res.text
    assert "준비 중 라운드" not in res.text


def _diagnosis(client, **fields):
    token = csrf_from(client.get("/diagnosis").text)
    data = {"csrf_token": token, **fields}
    return client.post("/diagnosis", data=data, follow_redirects=False)


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
    assert lead["monthly_cost"] == 1200000
    assert lead["has_elevator"] == 0
    assert lead["concerns"] == "청소, 소방 점검"
    assert lead["consent_marketing"] == 0
    assert lead["status"] == "신규"


def test_diagnosis_validation_errors(client, repo):
    res = _diagnosis(client, name="", phone="123", district="", building_type="성", consent_collect="on")
    assert res.status_code == 400
    for msg in ("이름을(를) 입력", "전화번호를 확인", "건물 위치", "건물 유형을(를) 골라"):
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


def test_round_detail_and_join_updates_count(client, repo, make_round):
    slug = make_round()
    page = client.get(f"/rounds/{slug}")
    assert page.status_code == 200
    assert "0채</strong> / 목표 10채" in page.text
    assert "3채</strong> 더 모이면" in page.text  # 0채일 때는 실제로 싸지는 3채 구간을 안내

    token = csrf_from(page.text)
    for i in range(3):
        res = client.post(f"/rounds/{slug}/join", data={
            **VALID_PERSON, "phone": f"0101234560{i}", "csrf_token": token,
            "consent_collect": "on", "consent_vendor_share": "on" if i == 0 else "",
            "current_cost": "45만",
        }, follow_redirects=False)
        assert res.status_code == 303

    page = client.get(f"/rounds/{slug}")
    assert "3채</strong> / 목표 10채" in page.text
    assert "2채</strong> 더 모이면" in page.text  # 5채 구간까지
    assert 'class="current"' in page.text

    rid = repo.get_round_by_slug(slug)["id"]
    parts = repo.list_participations(rid)
    assert [p["consent_vendor_share"] for p in parts] == [1, 0, 0]
    assert parts[0]["current_cost"] == 450000


def test_same_phone_cannot_inflate_count(client, repo, make_round):
    slug = make_round()
    token = csrf_from(client.get(f"/rounds/{slug}").text)
    form = {**VALID_PERSON, "csrf_token": token, "consent_collect": "on"}
    for phone in ("010-1234-5678", "01012345678", "010 1234 5678"):
        res = client.post(f"/rounds/{slug}/join", data={**form, "phone": phone}, follow_redirects=False)
        assert res.status_code == 303
    rid = repo.get_round_by_slug(slug)["id"]
    assert repo.participant_counts()[rid] == 1

    # 취소된 뒤에는 다시 신청할 수 있음
    [p] = repo.list_participations(rid)
    repo.update_participation(p["id"], "취소", "")
    client.post(f"/rounds/{slug}/join", data=form, follow_redirects=False)
    assert repo.participant_counts()[rid] == 1


def test_thanks_page_does_not_reveal_unpublished_round(client, make_round):
    slug = make_round(title="비공개 제목", status="draft")
    res = client.get(f"/thanks?kind=round&slug={slug}")
    assert res.status_code == 200
    assert "비공개 제목" not in res.text


def test_cancelled_participation_does_not_count(client, repo, make_round):
    slug = make_round()
    rid = repo.get_round_by_slug(slug)["id"]
    pid = repo.add_participation(rid, {"name": "a", "phone": "010-1-1", "district": "d",
                                        "building_type": "기타"})
    repo.update_participation(pid, "취소", "")
    assert repo.participant_counts().get(rid, 0) == 0


def test_draft_and_cancelled_rounds_are_hidden(client, make_round):
    for status in ("draft", "cancelled"):
        slug = make_round(status=status)
        assert client.get(f"/rounds/{slug}").status_code == 404


def test_closed_or_past_deadline_round_has_no_form_and_rejects_join(client, make_round):
    past = (today_kst() - timedelta(days=1)).isoformat()
    for slug in (make_round(status="closed"), make_round(deadline=past)):
        page = client.get(f"/rounds/{slug}")
        assert page.status_code == 200
        assert "참여 신청하기" not in page.text
        token = csrf_from(client.get("/diagnosis").text)
        res = client.post(f"/rounds/{slug}/join", data={**VALID_PERSON, "consent_collect": "on",
                                                         "csrf_token": token})
        assert res.status_code == 409


def test_static_pages(client):
    for path in ("/privacy", "/terms", "/rounds", "/thanks?kind=round"):
        assert client.get(path).status_code == 200
    assert client.get("/healthz").text == "ok"
