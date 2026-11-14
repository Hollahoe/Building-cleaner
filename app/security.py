"""보안 관련 도우미: CSRF 토큰, 관리자 로그인, 응답 보안 헤더, CSV 수식 주입 방지."""

from __future__ import annotations

import hmac
import secrets

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBasicCredentials
from starlette.datastructures import FormData

CSRF_COOKIE = "csrftoken"
CSRF_FIELD = "csrf_token"
ADMIN_USERNAME = "admin"

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'none'; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    ),
}


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def check_csrf(request: Request, form: FormData) -> None:
    """쿠키의 토큰과 폼의 토큰이 같아야 POST를 받습니다(이중 제출 방식)."""
    cookie = request.cookies.get(CSRF_COOKIE, "")
    sent = str(form.get(CSRF_FIELD) or "")
    if not cookie or not sent or not hmac.compare_digest(cookie, sent):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "요청을 확인할 수 없습니다. 페이지를 새로고침한 뒤 다시 시도해 주세요.")


def check_admin(credentials: HTTPBasicCredentials | None, admin_password: str) -> None:
    if not admin_password:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "관리자 비밀번호(ADMIN_PASSWORD)가 설정되지 않아 관리자 화면을 열 수 없습니다.",
        )
    ok = (
        credentials is not None
        and hmac.compare_digest(credentials.username.encode(), ADMIN_USERNAME.encode())
        and hmac.compare_digest(credentials.password.encode(), admin_password.encode())
    )
    if not ok:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "관리자 로그인이 필요합니다.",
            headers={"WWW-Authenticate": 'Basic realm="admin", charset="UTF-8"'},
        )


_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(value: object) -> str:
    """엑셀이 셀 값을 수식으로 실행하지 않도록 위험한 첫 글자 앞에 '를 붙입니다."""
    text = "" if value is None else str(value)
    if text.startswith(_FORMULA_PREFIXES):
        return "'" + text
    return text
