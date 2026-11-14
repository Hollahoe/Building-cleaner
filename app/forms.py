"""폼 입력 검증.

각 함수는 (정리된 값, 오류 메시지) 쌍을 돌려줍니다. 오류가 있으면 같은 폼을 다시
보여주면서 사용자가 입력한 값을 그대로 채워 둡니다.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from starlette.datastructures import FormData

from .db import LEAD_STATUSES, PARTICIPATION_STATUSES
from .rounds import ALLOWED_CATEGORIES, ROUND_STATUSES, TierError, parse_tiers, tiers_to_json

BUILDING_TYPES: tuple[str, ...] = (
    "꼬마빌딩(상가·사무실)",
    "상가주택",
    "원룸·다가구",
    "다세대·빌라",
    "기타",
)

CONCERNS: tuple[str, ...] = (
    "청소",
    "승강기",
    "소방 점검",
    "보험 만기 관리",
    "민원 응대",
    "누수·수선",
    "공실",
    "관리비 정산",
    "기타",
)

HONEYPOT_FIELD = "website"

Errors = dict[str, str]


def _text(form: FormData, name: str, label: str, errors: Errors, *, max_len: int,
          required: bool = False) -> str:
    value = str(form.get(name) or "").strip()
    if required and not value:
        errors[name] = f"{label}을(를) 입력해 주세요."
    elif len(value) > max_len:
        errors[name] = f"{label}은(는) {max_len}자 이내로 입력해 주세요."
    return value


def _choice(form: FormData, name: str, label: str, choices: tuple[str, ...], errors: Errors) -> str:
    value = str(form.get(name) or "").strip()
    if value not in choices:
        errors[name] = f"{label}을(를) 골라 주세요."
    return value


def parse_won(raw: str) -> int:
    """'45만', '450,000원', '450000' 같은 입력을 원 단위 정수로 바꿉니다."""
    text = raw.strip().replace(",", "").replace(" ", "").removesuffix("원")
    multiplier = 1
    if text.endswith("만"):
        text, multiplier = text[:-1], 10_000
    if not text:
        raise ValueError("empty")
    value = float(text) * multiplier
    if value < 0:
        raise ValueError("negative")
    return int(round(value))


def _money(form: FormData, name: str, label: str, errors: Errors) -> int | None:
    raw = str(form.get(name) or "").strip()
    if not raw:
        return None
    try:
        value = parse_won(raw)
    except ValueError:
        errors[name] = f"{label}은(는) 숫자로 적어 주세요. 예: 45만, 450000"
        return None
    if value > 100_000_000:
        errors[name] = f"{label}이(가) 너무 큽니다. 월 금액을 원 단위로 적어 주세요."
        return None
    return value


def _int(form: FormData, name: str, label: str, errors: Errors, *, lo: int, hi: int,
         required: bool = False) -> int | None:
    raw = str(form.get(name) or "").strip()
    if not raw:
        if required:
            errors[name] = f"{label}을(를) 입력해 주세요."
        return None
    try:
        value = int(raw)
    except ValueError:
        errors[name] = f"{label}은(는) 숫자로 적어 주세요."
        return None
    if not lo <= value <= hi:
        errors[name] = f"{label}은(는) {lo}~{hi} 사이로 적어 주세요."
        return None
    return value


def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw)
    if not re.fullmatch(r"0\d{8,10}", digits):
        return None
    if digits.startswith("02"):
        return f"02-{digits[2:-4]}-{digits[-4:]}"
    return f"{digits[:3]}-{digits[3:-4]}-{digits[-4:]}"


def _phone(form: FormData, errors: Errors) -> str:
    raw = str(form.get("phone") or "").strip()
    phone = normalize_phone(raw)
    if phone is None:
        errors["phone"] = "연락받을 전화번호를 확인해 주세요. 예: 010-1234-5678"
        return raw
    return phone


def _checked(form: FormData, name: str) -> bool:
    return str(form.get(name) or "") == "on"


def is_spam(form: FormData) -> bool:
    """사람에게는 보이지 않는 칸이 채워져 있으면 자동 입력 프로그램으로 봅니다."""
    return bool(str(form.get(HONEYPOT_FIELD) or "").strip())


def _contact_and_building(form: FormData, errors: Errors) -> dict[str, Any]:
    return {
        "name": _text(form, "name", "이름", errors, max_len=30, required=True),
        "phone": _phone(form, errors),
        "district": _text(form, "district", "건물 위치(구·동)", errors, max_len=40, required=True),
        "building_type": _choice(form, "building_type", "건물 유형", BUILDING_TYPES, errors),
        "floor_area": _text(form, "floor_area", "연면적", errors, max_len=20),
        "floors": _int(form, "floors", "층수", errors, lo=1, hi=60),
        "message": _text(form, "message", "남길 말", errors, max_len=1000),
        "consent_marketing": 1 if _checked(form, "consent_marketing") else 0,
    }


def _require_collect_consent(form: FormData, errors: Errors) -> None:
    if not _checked(form, "consent_collect"):
        errors["consent_collect"] = "개인정보 수집·이용에 동의해야 신청할 수 있습니다."


def validate_diagnosis(form: FormData) -> tuple[dict[str, Any], Errors]:
    errors: Errors = {}
    data = _contact_and_building(form, errors)
    elevator = str(form.get("has_elevator") or "")
    data["has_elevator"] = {"yes": 1, "no": 0}.get(elevator)
    data["monthly_cost"] = _money(form, "monthly_cost", "월 관리비", errors)
    concerns = [c for c in form.getlist("concerns") if c in CONCERNS]
    data["concerns"] = ", ".join(concerns)
    _require_collect_consent(form, errors)
    return data, errors


def validate_join(form: FormData) -> tuple[dict[str, Any], Errors]:
    errors: Errors = {}
    data = _contact_and_building(form, errors)
    data["current_cost"] = _money(form, "current_cost", "지금 내는 월 비용", errors)
    data["consent_vendor_share"] = 1 if _checked(form, "consent_vendor_share") else 0
    _require_collect_consent(form, errors)
    return data, errors


def _categories(form: FormData, errors: Errors, label: str = "항목") -> str:
    picked = [c for c in form.getlist("categories") if c in ALLOWED_CATEGORIES]
    if not picked:
        errors["categories"] = f"{label}을(를) 하나 이상 골라 주세요."
    return ", ".join(dict.fromkeys(picked))


def validate_demand(form: FormData, service_area: str,
                    service_dongs: tuple[str, ...]) -> tuple[dict[str, Any], Errors]:
    """공동구매 희망 등록. 동네는 목록에서 고르거나 직접 적습니다."""
    errors: Errors = {}
    data: dict[str, Any] = {
        "name": _text(form, "name", "이름", errors, max_len=30, required=True),
        "phone": _phone(form, errors),
        "building_type": _choice(form, "building_type", "건물 유형", BUILDING_TYPES, errors),
        "floor_area": _text(form, "floor_area", "연면적", errors, max_len=20),
        "floors": _int(form, "floors", "층수", errors, lo=1, hi=60),
        "current_cost": _money(form, "current_cost", "지금 내는 월 비용", errors),
        "message": _text(form, "message", "남길 말", errors, max_len=1000),
        "consent_marketing": 1 if _checked(form, "consent_marketing") else 0,
    }
    dong = str(form.get("dong") or "").strip()
    other = " ".join(str(form.get("area_other") or "").split())
    data["dong"], data["area_other"] = dong, other
    if dong and dong in service_dongs:
        data["area"] = f"{service_area} {dong}"
    elif other:
        if len(other) > 40:
            errors["area_other"] = "동네는 40자 이내로 적어 주세요."
        data["area"] = other
    else:
        errors["area_other" if not service_dongs else "dong"] = "건물이 있는 동네를 골라 주시거나 적어 주세요."
        data["area"] = ""
    data["categories"] = _categories(form, errors, "공동구매하고 싶은 항목")
    _require_collect_consent(form, errors)
    return data, errors


BULK_DISCOUNT_CHOICES: tuple[str, ...] = ("가능", "협의", "어려움")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def validate_partner(form: FormData) -> tuple[dict[str, Any], Errors]:
    """협력 업체 등록."""
    errors: Errors = {}
    data: dict[str, Any] = {
        "company": _text(form, "company", "상호", errors, max_len=60, required=True),
        "contact_name": _text(form, "contact_name", "담당자 이름", errors, max_len=30, required=True),
        "phone": _phone(form, errors),
        "email": _text(form, "email", "이메일", errors, max_len=120),
        "service_area": _text(form, "service_area", "작업 가능 지역", errors, max_len=100, required=True),
        "license_info": _text(form, "license_info", "등록·신고 정보", errors, max_len=200),
        "bulk_discount": _choice(form, "bulk_discount", "묶음 할인 가능 여부", BULK_DISCOUNT_CHOICES, errors),
        "message": _text(form, "message", "남길 말", errors, max_len=1000),
    }
    if data["email"] and not EMAIL_RE.fullmatch(data["email"]):
        errors["email"] = "이메일 주소를 확인해 주세요."
    data["categories"] = _categories(form, errors, "할 수 있는 용역")
    _require_collect_consent(form, errors)
    return data, errors


def validate_round(form: FormData) -> tuple[dict[str, Any], Errors]:
    errors: Errors = {}
    data: dict[str, Any] = {
        "title": _text(form, "title", "제목", errors, max_len=80, required=True),
        "category": _choice(form, "category", "항목", ALLOWED_CATEGORIES, errors),
        "district": _text(form, "district", "지역", errors, max_len=40, required=True),
        "summary": _text(form, "summary", "한 줄 소개", errors, max_len=200, required=True),
        "details": _text(form, "details", "상세 설명", errors, max_len=3000),
        "target_buildings": _int(form, "target_buildings", "목표 건물 수", errors,
                                 lo=1, hi=1000, required=True),
        "status": _choice(form, "status", "상태", tuple(ROUND_STATUSES), errors),
        "price_note": _text(form, "price_note", "가격 안내", errors, max_len=500, required=True),
        "fee_disclosure": _text(form, "fee_disclosure", "운영자 보수·업체 대가 공개", errors,
                                max_len=500, required=True),
    }
    raw_deadline = str(form.get("deadline") or "").strip()
    try:
        data["deadline"] = date.fromisoformat(raw_deadline).isoformat()
    except ValueError:
        errors["deadline"] = "마감일을 YYYY-MM-DD 형식으로 적어 주세요."
        data["deadline"] = raw_deadline
    tiers_text = str(form.get("tiers") or "")
    data["tiers_text"] = tiers_text
    try:
        data["tiers_json"] = tiers_to_json(parse_tiers(tiers_text))
    except TierError as exc:
        errors["tiers"] = str(exc)
        data["tiers_json"] = None
    return data, errors


def validate_status_update(form: FormData, statuses: tuple[str, ...]) -> tuple[str, str, Errors]:
    errors: Errors = {}
    status = _choice(form, "status", "상태", statuses, errors)
    memo = _text(form, "admin_memo", "메모", errors, max_len=2000)
    return status, memo, errors


LEAD_STATUS_CHOICES = LEAD_STATUSES
PARTICIPATION_STATUS_CHOICES = PARTICIPATION_STATUSES
