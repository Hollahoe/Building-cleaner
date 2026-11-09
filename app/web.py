"""웹 앱: 공개 페이지(창구·공동구매·희망 등록·업체 등록)와 관리자 화면."""

from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import forms
from .config import Settings, load_settings
from .db import (
    DEMAND_STATUSES,
    LEAD_STATUSES,
    PARTICIPATION_STATUSES,
    PARTNER_STATUSES,
    Repo,
    today_kst,
)
from .rounds import (
    ALLOWED_CATEGORIES,
    PUBLIC_STATUSES,
    ROUND_STATUSES,
    is_joinable,
    new_slug,
    progress_percent,
    tier_status,
    tiers_from_json,
    tiers_to_text,
)
from .security import (
    CSRF_COOKIE,
    CSRF_FIELD,
    SECURITY_HEADERS,
    check_admin,
    check_csrf,
    csv_safe,
    new_csrf_token,
)

BASE_DIR = Path(__file__).resolve().parent
BOARD_LIMIT = 8  # 첫 화면에 보여 줄 '모이고 있는 공동구매' 수


def won(value: int | None) -> str:
    return "-" if value is None else f"{value:,}원"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    repo = Repo(settings.database_path, settings.database_url)
    app = FastAPI(title=settings.brand_name, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.state.repo = repo
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    templates = Jinja2Templates(directory=BASE_DIR / "templates")
    templates.env.filters["won"] = won
    basic = HTTPBasic(auto_error=False)

    @app.middleware("http")
    async def csrf_cookie_and_headers(request: Request, call_next):
        token = request.cookies.get(CSRF_COOKIE, "")
        fresh = None
        if len(token) < 20:
            fresh = token = new_csrf_token()
        request.state.csrf_token = token
        response = await call_next(request)
        if fresh:
            response.set_cookie(
                CSRF_COOKIE, fresh, httponly=True, samesite="lax",
                secure=settings.cookie_secure, max_age=60 * 60 * 24 * 7,
            )
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        if request.url.path.startswith("/admin"):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
            response.headers["Cache-Control"] = "no-store"
        return response

    def render(request: Request, name: str, context: dict[str, Any] | None = None,
               status_code: int = 200) -> HTMLResponse:
        ctx = {
            "s": settings,
            "csrf_field": CSRF_FIELD,
            "csrf_token": request.state.csrf_token,
            "honeypot": forms.HONEYPOT_FIELD,
            "today": today_kst(),
            "categories": ALLOWED_CATEGORIES,
            "building_types": forms.BUILDING_TYPES,
        }
        ctx.update(context or {})
        return templates.TemplateResponse(request, name, ctx, status_code=status_code)

    def round_view(row, counts: dict[int, int] | None = None) -> dict[str, Any]:
        counts = repo.participant_counts() if counts is None else counts
        count = counts.get(row["id"], 0)
        tiers = tiers_from_json(row["tiers_json"])
        deadline = date.fromisoformat(row["deadline"])
        return {
            "row": row,
            "count": count,
            "tiers": tiers,
            "tier": tier_status(tiers, count),
            "progress": progress_percent(count, row["target_buildings"]),
            "deadline": deadline,
            "days_left": (deadline - today_kst()).days,
            "joinable": is_joinable(row["status"], deadline, today_kst()),
            "status_label": ROUND_STATUSES.get(row["status"], row["status"]),
        }

    def round_views(statuses: tuple[str, ...] | None) -> list[dict[str, Any]]:
        counts = repo.participant_counts()
        return [round_view(r, counts) for r in repo.list_rounds(statuses)]

    def board(limit: int | None = None) -> list[dict[str, Any]]:
        items = repo.demand_board()
        for item in items:
            item["remaining"] = max(0, settings.demand_threshold - item["count"])
            item["reached"] = item["count"] >= settings.demand_threshold
        return items[:limit] if limit else items

    def public_round_or_404(slug: str):
        row = repo.get_round_by_slug(slug)
        if row is None or row["status"] not in PUBLIC_STATUSES:
            raise HTTPException(404, "찾는 공동구매가 없습니다.")
        return row

    # ------------------------------------------------------------------ 공개 페이지
    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return render(request, "index.html", {
            "rounds": round_views(("open",)), "board": board(BOARD_LIMIT),
        })

    @app.get("/rounds", response_class=HTMLResponse)
    def rounds_list(request: Request):
        return render(request, "rounds.html", {
            "rounds": round_views(PUBLIC_STATUSES), "board": board(),
        })

    @app.get("/rounds/{slug}", response_class=HTMLResponse)
    def round_detail(request: Request, slug: str):
        view = round_view(public_round_or_404(slug))
        return render(request, "round_detail.html", {"r": view, "values": {}, "errors": {}})

    @app.post("/rounds/{slug}/join", response_class=HTMLResponse)
    async def round_join(request: Request, slug: str):
        form = await request.form()
        check_csrf(request, form)
        row = public_round_or_404(slug)
        view = round_view(row)
        if not view["joinable"]:
            raise HTTPException(409, "이 공동구매는 지금 참여 신청을 받지 않습니다.")
        if forms.is_spam(form):
            return RedirectResponse("/thanks?kind=round", status_code=303)
        data, errors = forms.validate_join(form)
        if errors:
            return render(request, "round_detail.html",
                          {"r": view, "values": data, "errors": errors}, status_code=400)
        # 같은 번호로 여러 번 신청해 참여 건물 수가 부풀려지지 않게 합니다.
        if not repo.has_active_participation(row["id"], data["phone"]):
            repo.add_participation(row["id"], data)
        return RedirectResponse(f"/thanks?kind=round&slug={row['slug']}", status_code=303)

    @app.get("/demand", response_class=HTMLResponse)
    def demand_form(request: Request, category: str = "", dong: str = ""):
        values = {"categories": category if category in ALLOWED_CATEGORIES else "",
                  "dong": dong if dong in settings.service_dongs else ""}
        return render(request, "demand.html", {"values": values, "errors": {}, "board": board()})

    @app.post("/demand", response_class=HTMLResponse)
    async def demand_submit(request: Request):
        form = await request.form()
        check_csrf(request, form)
        if forms.is_spam(form):
            return RedirectResponse("/thanks?kind=demand", status_code=303)
        data, errors = forms.validate_demand(form, settings.service_area, settings.service_dongs)
        if errors:
            return render(request, "demand.html",
                          {"values": data, "errors": errors, "board": board()}, status_code=400)
        repo.add_or_merge_demand(data)
        return RedirectResponse("/thanks?kind=demand", status_code=303)

    @app.get("/partners", response_class=HTMLResponse)
    def partner_form(request: Request):
        return render(request, "partners.html", {
            "values": {}, "errors": {}, "bulk_choices": forms.BULK_DISCOUNT_CHOICES,
        })

    @app.post("/partners", response_class=HTMLResponse)
    async def partner_submit(request: Request):
        form = await request.form()
        check_csrf(request, form)
        if forms.is_spam(form):
            return RedirectResponse("/thanks?kind=partner", status_code=303)
        data, errors = forms.validate_partner(form)
        if errors:
            return render(request, "partners.html", {
                "values": data, "errors": errors, "bulk_choices": forms.BULK_DISCOUNT_CHOICES,
            }, status_code=400)
        repo.add_partner(data)
        return RedirectResponse("/thanks?kind=partner", status_code=303)

    @app.get("/diagnosis", response_class=HTMLResponse)
    def diagnosis_form(request: Request):
        return render(request, "diagnosis.html", {
            "values": {}, "errors": {}, "concerns": forms.CONCERNS, "selected": [],
        })

    @app.post("/diagnosis", response_class=HTMLResponse)
    async def diagnosis_submit(request: Request):
        form = await request.form()
        check_csrf(request, form)
        if forms.is_spam(form):
            return RedirectResponse("/thanks?kind=diagnosis", status_code=303)
        data, errors = forms.validate_diagnosis(form)
        if errors:
            return render(request, "diagnosis.html", {
                "values": data, "errors": errors, "concerns": forms.CONCERNS,
                "selected": form.getlist("concerns"),
            }, status_code=400)
        repo.add_lead(data)
        return RedirectResponse("/thanks?kind=diagnosis", status_code=303)

    @app.get("/thanks", response_class=HTMLResponse)
    def thanks(request: Request, kind: str = "diagnosis", slug: str = ""):
        row = repo.get_round_by_slug(slug) if slug else None
        if row is not None and row["status"] not in PUBLIC_STATUSES:
            row = None
        return render(request, "thanks.html", {"kind": kind, "round": row})

    @app.get("/privacy", response_class=HTMLResponse)
    def privacy(request: Request):
        return render(request, "privacy.html")

    @app.get("/terms", response_class=HTMLResponse)
    def terms(request: Request):
        return render(request, "terms.html")

    @app.get("/healthz", response_class=PlainTextResponse)
    def healthz():
        return "ok"

    # ------------------------------------------------------------------ 관리자
    def require_admin(credentials: HTTPBasicCredentials | None = Depends(basic)) -> None:
        check_admin(credentials, settings.admin_password)

    admin = [Depends(require_admin)]

    @app.get("/admin", response_class=HTMLResponse, dependencies=admin)
    def admin_home(request: Request):
        return render(request, "admin/home.html", {
            "lead_counts": repo.lead_status_counts(), "rounds": round_views(None),
            "board": board(), "partner_count": len(repo.list_partners()),
        })

    async def _status_update(request: Request, table: str, row_id: int,
                             statuses: tuple[str, ...]) -> None:
        form = await request.form()
        check_csrf(request, form)
        status, memo, errors = forms.validate_status_update(form, statuses)
        if errors or not repo.update_status(table, row_id, status, memo):
            raise HTTPException(400, "저장하지 못했습니다. 입력값을 확인해 주세요.")

    @app.get("/admin/leads", response_class=HTMLResponse, dependencies=admin)
    def admin_leads(request: Request):
        return render(request, "admin/leads.html", {
            "leads": repo.list_leads(), "statuses": LEAD_STATUSES,
        })

    @app.post("/admin/leads/{lead_id}", dependencies=admin)
    async def admin_lead_update(request: Request, lead_id: int):
        await _status_update(request, "leads", lead_id, LEAD_STATUSES)
        return RedirectResponse(f"/admin/leads#lead-{lead_id}", status_code=303)

    @app.get("/admin/demand", response_class=HTMLResponse, dependencies=admin)
    def admin_demand(request: Request):
        return render(request, "admin/demand.html", {
            "demands": repo.list_demands(), "statuses": DEMAND_STATUSES, "board": board(),
        })

    @app.post("/admin/demand/{demand_id}", dependencies=admin)
    async def admin_demand_update(request: Request, demand_id: int):
        await _status_update(request, "demands", demand_id, DEMAND_STATUSES)
        return RedirectResponse(f"/admin/demand#d-{demand_id}", status_code=303)

    @app.get("/admin/partners", response_class=HTMLResponse, dependencies=admin)
    def admin_partners(request: Request):
        return render(request, "admin/partners.html", {
            "partners": repo.list_partners(), "statuses": PARTNER_STATUSES,
        })

    @app.post("/admin/partners/{partner_id}", dependencies=admin)
    async def admin_partner_update(request: Request, partner_id: int):
        await _status_update(request, "partners", partner_id, PARTNER_STATUSES)
        return RedirectResponse(f"/admin/partners#pt-{partner_id}", status_code=303)

    def round_form_context(values: dict, errors: dict, round_row=None) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "values": values, "errors": errors, "round": round_row,
            "round_statuses": ROUND_STATUSES,
        }
        if round_row is not None:
            ctx.update({
                "view": round_view(round_row),
                "participations": repo.list_participations(round_row["id"]),
                "participation_statuses": PARTICIPATION_STATUSES,
            })
        return ctx

    @app.get("/admin/rounds/new", response_class=HTMLResponse, dependencies=admin)
    def admin_round_new(request: Request, category: str = "", area: str = ""):
        values = {
            "status": "draft",
            "category": category if category in ALLOWED_CATEGORIES else "",
            "district": area[:40] or settings.service_area,
            "tiers_text": "1=\n3=\n5=\n10=",
            "price_note": "업체 견적을 바탕으로 한 예상 단가입니다. 최종 금액은 건물별 현장 확인 뒤 정해지고, "
                          "계약은 건물주님과 업체가 직접 맺습니다.",
            "fee_disclosure": "운영자가 업체로부터 받는 대가: 없음. 운영자 보수는 건물주님과의 계약에 따릅니다.",
        }
        return render(request, "admin/round_form.html", round_form_context(values, {}))

    @app.post("/admin/rounds", response_class=HTMLResponse, dependencies=admin)
    async def admin_round_create(request: Request):
        form = await request.form()
        check_csrf(request, form)
        data, errors = forms.validate_round(form)
        if errors:
            return render(request, "admin/round_form.html",
                          round_form_context(data, errors), status_code=400)
        round_id = repo.add_round(data, new_slug(today_kst()))
        return RedirectResponse(f"/admin/rounds/{round_id}", status_code=303)

    @app.get("/admin/rounds/{round_id}", response_class=HTMLResponse, dependencies=admin)
    def admin_round_edit(request: Request, round_id: int):
        row = repo.get_round(round_id)
        if row is None:
            raise HTTPException(404, "라운드가 없습니다.")
        values = dict(row)
        values["tiers_text"] = tiers_to_text(tiers_from_json(row["tiers_json"]))
        return render(request, "admin/round_form.html", round_form_context(values, {}, row))

    @app.post("/admin/rounds/{round_id}", response_class=HTMLResponse, dependencies=admin)
    async def admin_round_update(request: Request, round_id: int):
        form = await request.form()
        check_csrf(request, form)
        row = repo.get_round(round_id)
        if row is None:
            raise HTTPException(404, "라운드가 없습니다.")
        data, errors = forms.validate_round(form)
        if errors:
            return render(request, "admin/round_form.html",
                          round_form_context(data, errors, row), status_code=400)
        repo.update_round(round_id, data)
        return RedirectResponse(f"/admin/rounds/{round_id}", status_code=303)

    @app.post("/admin/participations/{participation_id}", dependencies=admin)
    async def admin_participation_update(request: Request, participation_id: int):
        row = repo.get_participation(participation_id)
        if row is None:
            raise HTTPException(400, "저장하지 못했습니다. 입력값을 확인해 주세요.")
        await _status_update(request, "participations", participation_id, PARTICIPATION_STATUSES)
        return RedirectResponse(f"/admin/rounds/{row['round_id']}#p-{participation_id}",
                                status_code=303)

    # ---- CSV 내보내기 ------------------------------------------------------
    def csv_response(filename: str, header: list[str], rows: list[list[Any]]) -> Response:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(header)
        for r in rows:
            writer.writerow([csv_safe(v) for v in r])
        # 엑셀에서 한글이 깨지지 않도록 UTF-8 BOM을 붙입니다.
        return Response(
            "﻿" + buf.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    def yes_no(v: int | None) -> str:
        return "예" if v else "아니오"

    @app.get("/admin/export/leads.csv", dependencies=admin)
    def export_leads():
        header = ["id", "신청일시", "이름", "연락처", "건물 위치", "건물 유형", "연면적", "층수",
                  "승강기", "월 관리비(원)", "고민 항목", "남긴 말", "소식 수신 동의", "상태", "메모"]
        rows = [[
            r["id"], r["created_at"], r["name"], r["phone"], r["district"], r["building_type"],
            r["floor_area"], r["floors"],
            {1: "있음", 0: "없음"}.get(r["has_elevator"], ""), r["monthly_cost"], r["concerns"],
            r["message"], yes_no(r["consent_marketing"]), r["status"], r["admin_memo"],
        ] for r in repo.list_leads()]
        return csv_response("leads.csv", header, rows)

    @app.get("/admin/export/demand.csv", dependencies=admin)
    def export_demand():
        header = ["id", "등록일시", "이름", "연락처", "동네", "희망 항목", "건물 유형", "연면적",
                  "층수", "지금 월 비용(원)", "남긴 말", "소식 수신 동의", "상태", "메모"]
        rows = [[
            d["id"], d["created_at"], d["name"], d["phone"], d["area"], d["categories"],
            d["building_type"], d["floor_area"], d["floors"], d["current_cost"], d["message"],
            yes_no(d["consent_marketing"]), d["status"], d["admin_memo"],
        ] for d in repo.list_demands()]
        return csv_response("demand.csv", header, rows)

    @app.get("/admin/export/partners.csv", dependencies=admin)
    def export_partners():
        header = ["id", "등록일시", "상호", "담당자", "연락처", "이메일", "용역 항목", "작업 지역",
                  "등록·신고 정보", "묶음 할인", "남긴 말", "상태", "메모"]
        rows = [[
            p["id"], p["created_at"], p["company"], p["contact_name"], p["phone"], p["email"],
            p["categories"], p["service_area"], p["license_info"], p["bulk_discount"],
            p["message"], p["status"], p["admin_memo"],
        ] for p in repo.list_partners()]
        return csv_response("partners.csv", header, rows)

    @app.get("/admin/export/rounds/{round_id}/participants.csv", dependencies=admin)
    def export_participants(round_id: int):
        if repo.get_round(round_id) is None:
            raise HTTPException(404, "라운드가 없습니다.")
        header = ["id", "신청일시", "이름", "연락처", "건물 위치", "건물 유형", "연면적", "층수",
                  "지금 월 비용(원)", "업체 정보 제공 동의", "소식 수신 동의", "남긴 말", "상태", "메모"]
        rows = [[
            p["id"], p["created_at"], p["name"], p["phone"], p["district"], p["building_type"],
            p["floor_area"], p["floors"], p["current_cost"], yes_no(p["consent_vendor_share"]),
            yes_no(p["consent_marketing"]), p["message"], p["status"], p["admin_memo"],
        ] for p in repo.list_participations(round_id)]
        return csv_response(f"round-{round_id}-participants.csv", header, rows)

    return app
