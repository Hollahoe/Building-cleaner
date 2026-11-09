"""공동구매 라운드의 규칙: 허용 항목, 상태, 묶음 단가 구간 계산.

웹 프레임워크와 DB에 의존하지 않는 순수 함수만 둡니다(테스트하기 쉽게).
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import date

# 공동구매로 묶을 수 있는 항목.
# 보험·세무·법률·임대차 중개는 넣지 않습니다. 자격 없이 소개·알선하고 대가를 받으면
# 법 위반이 될 수 있습니다(docs/legal-checklist.md).
ALLOWED_CATEGORIES: tuple[str, ...] = (
    "청소",
    "승강기 유지보수",
    "소방 점검",
    "CCTV·보안",
    "방역",
    "저수조·정화조 청소",
    "기타 시설 용역",
)

ROUND_STATUSES: dict[str, str] = {
    "draft": "준비 중",
    "open": "모집 중",
    "closed": "모집 마감",
    "succeeded": "성사",
    "cancelled": "취소",
}

# 방문자에게 보이는 상태. draft·cancelled 라운드는 공개 페이지에 나오지 않습니다.
PUBLIC_STATUSES: tuple[str, ...] = ("open", "closed", "succeeded")


@dataclass(frozen=True)
class Tier:
    """`min_buildings`채 이상 모이면 1채당 월 `price`원."""

    min_buildings: int
    price: int


class TierError(ValueError):
    """관리자가 입력한 단가 구간이 잘못됐을 때."""


def _to_int(text: str) -> int:
    cleaned = text.strip().replace(",", "").replace("원", "").replace("채", "").strip()
    return int(cleaned)


def parse_tiers(text: str) -> list[Tier]:
    """관리자 입력 `건물 수=1채당 월 단가` 줄들을 구간 목록으로 바꿉니다.

    예: "1=450000\\n3=420000\\n10=380000"
    """
    tiers: list[Tier] = []
    seen: set[int] = set()
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if "=" not in line:
            raise TierError(f"{lineno}번째 줄: '건물 수=1채당 월 단가' 형식으로 적어 주세요.")
        left, right = line.split("=", 1)
        try:
            n = _to_int(left)
            price = _to_int(right)
        except ValueError:
            raise TierError(f"{lineno}번째 줄: 숫자만 적어 주세요.") from None
        if not 1 <= n <= 1000:
            raise TierError(f"{lineno}번째 줄: 건물 수는 1~1000 사이여야 합니다.")
        if not 0 < price <= 100_000_000:
            raise TierError(f"{lineno}번째 줄: 단가는 1원~1억 원 사이여야 합니다.")
        if n in seen:
            raise TierError(f"{lineno}번째 줄: {n}채 구간이 두 번 나옵니다.")
        seen.add(n)
        tiers.append(Tier(n, price))
    if not tiers:
        raise TierError("단가 구간을 하나 이상 적어 주세요.")
    tiers.sort(key=lambda t: t.min_buildings)
    if tiers[0].min_buildings != 1:
        raise TierError("첫 구간은 1채(혼자 계약할 때 단가)부터 적어 주세요.")
    return tiers


def tiers_to_json(tiers: list[Tier]) -> str:
    return json.dumps([{"min": t.min_buildings, "price": t.price} for t in tiers])


def tiers_from_json(raw: str) -> list[Tier]:
    return [Tier(int(item["min"]), int(item["price"])) for item in json.loads(raw)]


def tiers_to_text(tiers: list[Tier]) -> str:
    return "\n".join(f"{t.min_buildings}={t.price}" for t in tiers)


@dataclass(frozen=True)
class TierStatus:
    current: Tier | None  # 지금 인원으로 적용되는 구간 (0채면 없음)
    next: Tier | None  # 다음 구간 (마지막 구간에 도달했으면 없음)
    remaining: int  # 다음 구간까지 더 필요한 건물 수
    saving_vs_single: int  # 혼자 계약할 때보다 1채당 월 얼마 싼지


def tier_status(tiers: list[Tier], count: int) -> TierStatus:
    """`next`는 혼자 계약할 때보다 실제로 싸지는 다음 구간입니다.

    0채일 때 '1채 더 모이면 (혼자 단가)'처럼 의미 없는 안내가 나가지 않게 합니다.
    """
    current: Tier | None = None
    nxt: Tier | None = None
    single = tiers[0].price
    for t in tiers:
        if t.min_buildings <= count:
            current = t
        elif nxt is None and t.price < single:
            nxt = t
    remaining = nxt.min_buildings - count if nxt else 0
    saving = tiers[0].price - current.price if current else 0
    return TierStatus(current=current, next=nxt, remaining=remaining, saving_vs_single=saving)


def progress_percent(count: int, target: int) -> int:
    if target <= 0:
        return 0
    return min(100, round(count * 100 / target))


def is_joinable(status: str, deadline: date, today: date) -> bool:
    return status == "open" and today <= deadline


def new_slug(today: date) -> str:
    return f"{today:%Y%m%d}-{secrets.token_hex(3)}"
