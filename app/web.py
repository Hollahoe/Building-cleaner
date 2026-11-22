"""웹 앱: 공개 페이지(창구·상담 신청·업체 등록)와 관리자 화면."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import forms
from .config import Settings, load_settings
from .db import LEAD_STATUSES, PARTNER_STATUSES, Repo
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
            "categories": forms.PARTNER_CATEGORIES,
            "building_types": forms.BUILDING_TYPES,
        }
        ctx.update(context or {})
        return templates.TemplateResponse(request, name, ctx, status_code=status_code)

    # ------------------------------------------------------------------ 공개 페이지
    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return render(request, "index.html")

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
    def thanks(request: Request, kind: str = "diagnosis"):
        return render(request, "thanks.html", {"kind": kind})

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
            "lead_counts": repo.lead_status_counts(), "partner_count": len(repo.list_partners()),
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

    @app.get("/admin/partners", response_class=HTMLResponse, dependencies=admin)
    def admin_partners(request: Request):
        return render(request, "admin/partners.html", {
            "partners": repo.list_partners(), "statuses": PARTNER_STATUSES,
        })

    @app.post("/admin/partners/{partner_id}", dependencies=admin)
    async def admin_partner_update(request: Request, partner_id: int):
        await _status_update(request, "partners", partner_id, PARTNER_STATUSES)
        return RedirectResponse(f"/admin/partners#pt-{partner_id}", status_code=303)

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
        header = ["id", "신청일시", "이름", "연락처", "건물 주소", "건물 유형", "연면적", "층수",
                  "승강기", "월 관리비(원)", "고민 항목", "남긴 말", "소식 수신 동의", "상태", "메모"]
        rows = [[
            r["id"], r["created_at"], r["name"], r["phone"], r["district"], r["building_type"],
            r["floor_area"], r["floors"],
            {1: "있음", 0: "없음"}.get(r["has_elevator"], ""), r["monthly_cost"], r["concerns"],
            r["message"], yes_no(r["consent_marketing"]), r["status"], r["admin_memo"],
        ] for r in repo.list_leads()]
        return csv_response("leads.csv", header, rows)

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

    return app
