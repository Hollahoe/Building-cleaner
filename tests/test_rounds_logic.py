import pytest

from app.forms import normalize_phone, parse_won
from app.rounds import (
    ALLOWED_CATEGORIES,
    Tier,
    TierError,
    parse_tiers,
    progress_percent,
    tier_status,
    tiers_from_json,
    tiers_to_json,
    tiers_to_text,
)

TIERS = [Tier(1, 450000), Tier(3, 420000), Tier(5, 400000), Tier(10, 380000)]


def test_parse_tiers_sorts_and_accepts_commas_and_units():
    assert parse_tiers("5=400,000원\n1=450000\n3채=420000\n\n10=380000") == TIERS


@pytest.mark.parametrize("text, message", [
    ("", "하나 이상"),
    ("3=420000", "1채"),
    ("1=450000\n1=440000", "두 번"),
    ("1-450000", "형식"),
    ("1=abc", "숫자"),
    ("0=450000", "1~1000"),
    ("1=0", "1원"),
])
def test_parse_tiers_rejects_bad_input(text, message):
    with pytest.raises(TierError, match=message):
        parse_tiers(text)


def test_tiers_round_trip():
    assert tiers_from_json(tiers_to_json(TIERS)) == TIERS
    assert parse_tiers(tiers_to_text(TIERS)) == TIERS


@pytest.mark.parametrize("count, current, nxt, remaining, saving", [
    (0, None, 3, 3, 0),
    (1, 1, 3, 2, 0),
    (2, 1, 3, 1, 0),
    (3, 3, 5, 2, 30000),
    (9, 5, 10, 1, 50000),
    (10, 10, None, 0, 70000),
    (25, 10, None, 0, 70000),
])
def test_tier_status(count, current, nxt, remaining, saving):
    st = tier_status(TIERS, count)
    assert (st.current.min_buildings if st.current else None) == current
    assert (st.next.min_buildings if st.next else None) == nxt
    assert st.remaining == remaining
    assert st.saving_vs_single == saving


def test_next_tier_skips_tiers_that_are_not_cheaper():
    flat = [Tier(1, 400000), Tier(3, 400000), Tier(5, 350000)]
    st = tier_status(flat, 1)
    assert st.next == Tier(5, 350000) and st.remaining == 4
    assert tier_status([Tier(1, 400000)], 0).next is None


def test_progress_percent_caps_at_100():
    assert progress_percent(3, 10) == 30
    assert progress_percent(15, 10) == 100
    assert progress_percent(1, 0) == 0


def test_no_insurance_tax_legal_or_brokerage_categories():
    banned = ("보험", "세무", "법률", "중개")
    assert not [c for c in ALLOWED_CATEGORIES if any(b in c for b in banned)]


@pytest.mark.parametrize("raw, expected", [
    ("45만", 450000), ("450,000원", 450000), ("1.5만", 15000), ("120만원", 1200000), ("0", 0),
])
def test_parse_won(raw, expected):
    assert parse_won(raw) == expected


@pytest.mark.parametrize("raw", ["", "만", "-3", "abc"])
def test_parse_won_rejects(raw):
    with pytest.raises(ValueError):
        parse_won(raw)


@pytest.mark.parametrize("raw, expected", [
    ("01012345678", "010-1234-5678"),
    ("010-1234-5678", "010-1234-5678"),
    ("0212345678", "02-1234-5678"),
    ("021234567", "02-123-4567"),
    ("0311234567", "031-123-4567"),
    ("12345", None),
    ("1012345678", None),
])
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected
