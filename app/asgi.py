"""서버 실행 진입점: `uvicorn app.asgi:app`.

환경 변수에서 설정을 읽어 앱을 만듭니다. 테스트는 `create_app(settings)`를 직접 씁니다.
"""

from .main import create_app

app = create_app()
