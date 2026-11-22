"""서버 실행 진입점.

- 로컬·Docker: `uvicorn app.asgi:app`
- Vercel: `app/` 폴더의 `asgi.py`에 있는 `app`을 자동으로 찾아 실행합니다.

환경 변수에서 설정을 읽어 앱을 만듭니다. 테스트는 `create_app(settings)`를 직접 씁니다.
"""

from fastapi import FastAPI

from .web import create_app

app: FastAPI = create_app()
