"""화면 확인용 예시 공동구매를 넣습니다. 실제 운영 DB에는 쓰지 마세요.

    python -m app.seed --demo

제목 앞에 [예시]가 붙고, 금액은 가상 숫자입니다(sourcing/vendors.csv의 예시 행과 같음).
"""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta

from .config import load_settings
from .db import Repo, today_kst
from .rounds import new_slug, parse_tiers, tiers_to_json


def seed_demo(repo: Repo) -> int:
    today = today_kst()
    data = {
        "title": "[예시] 망원동 계단·복도 청소 공동구매 1차",
        "category": "청소",
        "district": "마포구 망원동",
        "summary": "주 2회 계단·복도·공용 화장실 청소를 이웃 건물과 함께 계약합니다.",
        "details": "작업 범위: 계단·복도·공용 화장실, 분리수거장 정리\n주기: 주 2회\n포함: 소모품(화장지·세제·봉투)\n제외: 유리창 청소(별도 견적)",
        "target_buildings": 10,
        "deadline": (today + timedelta(days=21)).isoformat(),
        "status": "open",
        "tiers_json": tiers_to_json(parse_tiers("1=450000\n3=420000\n5=400000\n10=380000")),
        "price_note": "예시 화면입니다. 금액은 가상 숫자이며 실제 견적이 아닙니다.",
        "fee_disclosure": "운영자가 업체로부터 받는 대가: 없음. 운영자 보수는 건물주님과의 계약에 따릅니다.",
    }
    return repo.add_round(data, new_slug(today))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="예시 공동구매 1개를 넣습니다")
    args = parser.parse_args(argv)
    if not args.demo:
        parser.print_help()
        return 1
    settings = load_settings()
    round_id = seed_demo(Repo(settings.database_path))
    print(f"예시 공동구매를 만들었습니다 (id={round_id}, DB={settings.database_path}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
