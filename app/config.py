"""환경 변수로 바꾸는 설정.

브랜드 이름, 연락처, 관리자 비밀번호처럼 운영하면서 바뀌는 값은 코드가 아니라
환경 변수로 넣습니다. 값의 의미는 `.env.example`에 정리돼 있습니다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    brand_name: str = "빌딩모아관리"
    service_area: str = "마포구"
    # 공동구매 희망 등록에서 고르는 동네 목록. 비어 있으면 직접 입력만 받습니다.
    service_dongs: tuple[str, ...] = ()
    # 같은 동네·같은 항목에 이만큼 모이면 업체 견적을 받아 공동구매를 엽니다.
    demand_threshold: int = 5
    contact_phone: str = ""
    contact_email: str = ""
    kakao_url: str = ""
    business_info: str = "사업자 정보는 사업자등록 후 기재합니다."
    fee_text: str = "줄어든 운영비의 일부만 보수로 받습니다. 줄지 않으면 받지 않습니다."
    privacy_officer: str = ""
    admin_password: str = ""
    # Supabase 등 Postgres 연결 주소. 있으면 SQLite 대신 이걸 씁니다.
    database_url: str = ""
    database_path: str = "data/app.db"
    cookie_secure: bool = False


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def _env_list(name: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in os.getenv(name, "").split(",") if x.strip())


def load_settings() -> Settings:
    d = Settings()
    settings = Settings(
        brand_name=os.getenv("BRAND_NAME", d.brand_name),
        service_area=os.getenv("SERVICE_AREA", d.service_area),
        service_dongs=_env_list("SERVICE_DONGS"),
        demand_threshold=max(1, _env_int("DEMAND_THRESHOLD", d.demand_threshold)),
        contact_phone=os.getenv("CONTACT_PHONE", d.contact_phone),
        contact_email=os.getenv("CONTACT_EMAIL", d.contact_email),
        kakao_url=os.getenv("KAKAO_URL", d.kakao_url),
        business_info=os.getenv("BUSINESS_INFO", d.business_info),
        fee_text=os.getenv("FEE_TEXT", d.fee_text),
        privacy_officer=os.getenv("PRIVACY_OFFICER", d.privacy_officer),
        admin_password=os.getenv("ADMIN_PASSWORD", d.admin_password),
        database_url=os.getenv("DATABASE_URL", d.database_url),
        database_path=os.getenv("DATABASE_PATH", d.database_path),
        cookie_secure=_env_bool("COOKIE_SECURE", d.cookie_secure),
    )
    # Vercel 함수의 파일은 저장이 유지되지 않으므로 SQLite로 돌리면 신청 기록이 사라집니다.
    if os.getenv("VERCEL") and not settings.database_url:
        raise RuntimeError(
            "Vercel에서는 DATABASE_URL(Supabase 연결 주소)을 환경 변수로 넣어야 합니다. "
            "docs/deploy-guide.md 3단계를 보세요."
        )
    return settings
