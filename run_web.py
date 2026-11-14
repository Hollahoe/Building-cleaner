"""이 컴퓨터에서 웹 창구를 실행하는 시작 파일.

    python run_web.py              # http://127.0.0.1:8000
    python run_web.py --reload     # 코드를 고치면 자동으로 다시 시작
    python run_web.py --port 8010

- Visual Studio: 이 파일을 '시작 항목으로 설정'한 뒤 F5.
- VS Code: 실행 및 디버그에서 '웹 창구 실행'을 고르고 F5.

같은 폴더에 `.env` 파일이 있으면 읽어서 환경 변수로 씁니다(`.env.example`을 복사해 만듭니다).
이미 설정된 환경 변수는 덮어쓰지 않고, 값이 빈 줄은 건너뜁니다.
배포(Vercel·Docker)는 이 파일을 쓰지 않고 `app.asgi:app`을 바로 실행합니다.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_env_file(path: Path) -> list[str]:
    """`KEY=VALUE` 줄을 환경 변수로 넣고, 넣은 이름 목록을 돌려줍니다.

    주석(#)과 빈 줄, 값이 빈 줄, 이미 환경 변수에 있는 이름은 건너뜁니다.
    값을 감싼 따옴표 한 쌍은 벗깁니다. 메모장이 붙이는 BOM도 처리합니다.
    """
    loaded: list[str] = []
    if not path.is_file():
        return loaded
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and value and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="빌딩모아관리 웹 창구를 이 컴퓨터에서 실행합니다.")
    parser.add_argument("--host", default="127.0.0.1", help="기본 127.0.0.1 (이 컴퓨터에서만 접속)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="코드를 고치면 자동으로 다시 시작")
    args = parser.parse_args(argv)

    # 한글을 못 쓰는 콘솔(영문 Windows 등)에서도 안내 문구 때문에 멈추지 않게 합니다.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")

    # data/app.db 같은 상대 경로가 어느 폴더에서 실행해도 같은 곳을 가리키게 합니다.
    os.chdir(ROOT)
    loaded = load_env_file(ROOT / ".env")

    import uvicorn

    print(f"주소: http://{args.host}:{args.port}  (관리자: /admin, 아이디 admin)")
    if loaded:
        print(f".env에서 읽은 설정: {', '.join(loaded)}")
    if not os.environ.get("ADMIN_PASSWORD"):
        print("ADMIN_PASSWORD가 없어 관리자 화면은 잠겨 있습니다. .env에 넣으세요.")
    uvicorn.run("app.asgi:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
