"""환경 변수로 바꾸는 설정.

브랜드 이름, 연락처, 관리자 비밀번호처럼 운영하면서 바뀌는 값은 코드가 아니라
환경 변수로 넣습니다. 값의 의미는 `.env.example`에 정리돼 있습니다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    brand_name: str = "모아관리(가칭)"
    service_area: str = "마포구"
    contact_phone: str = ""
    contact_email: str = ""
    kakao_url: str = ""
    business_info: str = "사업자 정보는 사업자등록 후 기재합니다."
    fee_text: str = "줄어든 운영비의 일부만 보수로 받습니다. 줄지 않으면 받지 않습니다."
    privacy_officer: str = ""
    admin_password: str = ""
    database_path: str = "data/app.db"
    cookie_secure: bool = False


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    d = Settings()
    return Settings(
        brand_name=os.getenv("BRAND_NAME", d.brand_name),
        service_area=os.getenv("SERVICE_AREA", d.service_area),
        contact_phone=os.getenv("CONTACT_PHONE", d.contact_phone),
        contact_email=os.getenv("CONTACT_EMAIL", d.contact_email),
        kakao_url=os.getenv("KAKAO_URL", d.kakao_url),
        business_info=os.getenv("BUSINESS_INFO", d.business_info),
        fee_text=os.getenv("FEE_TEXT", d.fee_text),
        privacy_officer=os.getenv("PRIVACY_OFFICER", d.privacy_officer),
        admin_password=os.getenv("ADMIN_PASSWORD", d.admin_password),
        database_path=os.getenv("DATABASE_PATH", d.database_path),
        cookie_secure=_env_bool("COOKIE_SECURE", d.cookie_secure),
    )
