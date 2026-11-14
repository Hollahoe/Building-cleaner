"""run_web.py의 .env 읽기."""

import run_web


def test_load_env_file_sets_values_and_strips_quotes(tmp_path, monkeypatch):
    for name in ("BM_TEST_A", "BM_TEST_B", "BM_TEST_C", "BM_TEST_EMPTY"):
        monkeypatch.delenv(name, raising=False)
    env = tmp_path / ".env"
    # 메모장이 붙이는 BOM, 주석, 빈 값, 따옴표, 값 안의 '='
    env.write_text(
        "# 주석\n"
        "BM_TEST_A=마포구\n"
        "BM_TEST_B=\"따옴표 값\"\n"
        "BM_TEST_C=postgresql://u:p@host:6543/db?sslmode=require\n"
        "BM_TEST_EMPTY=\n"
        "\n"
        "줄에 등호 없음\n",
        encoding="utf-8-sig",
    )

    loaded = run_web.load_env_file(env)

    import os

    assert loaded == ["BM_TEST_A", "BM_TEST_B", "BM_TEST_C"]
    assert os.environ["BM_TEST_A"] == "마포구"
    assert os.environ["BM_TEST_B"] == "따옴표 값"
    assert os.environ["BM_TEST_C"] == "postgresql://u:p@host:6543/db?sslmode=require"
    assert "BM_TEST_EMPTY" not in os.environ
    for name in loaded:
        monkeypatch.delenv(name, raising=False)


def test_load_env_file_keeps_existing_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("BM_TEST_KEEP", "이미 있는 값")
    env = tmp_path / ".env"
    env.write_text("BM_TEST_KEEP=파일 값\n", encoding="utf-8")

    assert run_web.load_env_file(env) == []

    import os

    assert os.environ["BM_TEST_KEEP"] == "이미 있는 값"


def test_load_env_file_missing_file_is_fine(tmp_path):
    assert run_web.load_env_file(tmp_path / "없는파일.env") == []
