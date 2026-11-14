# Visual Studio · VS Code에서 열기

이 레포를 내 컴퓨터로 가져와 Visual Studio 또는 VS Code에서 열고 웹 창구를 실행하는 방법입니다.

> **확인 수준 (2026-11-14)**
> - 클라우드(리눅스, Python 3.13)에서 `python run_web.py` 실행과 테스트 73개 통과를 확인했습니다.
> - Windows는 직접 실행해 보지 못했습니다. 필요한 패키지가 Windows용으로 모두 있는지만 Python 3.11·3.12·3.13·3.14에 대해 확인했습니다.
> - Visual Studio와 VS Code 프로그램 안에서는 실행해 보지 못했습니다. 두 제품의 공식 문서 사이트도 이 환경에서 열리지 않아, 설정 형식은 검색 결과를 따랐습니다. 메뉴 이름이 다르면 영어 이름을 기준으로 찾으세요.

## 1. 준비물

- **Git**
- **Python 3.11–3.14** (설치할 때 PATH에 추가하는 옵션을 켜세요)
- **VS Code** 또는 **Visual Studio 2022** 가운데 하나

## 2. 내려받기

터미널(Windows는 PowerShell)에서 실행합니다.

```
git clone -b claude/elegant-einstein-ihy8sw https://github.com/Hollahoe/Building-cleaner.git
cd Building-cleaner
```

- PR이 `main`에 병합된 뒤에는 `-b claude/elegant-einstein-ihy8sw`를 빼고 받으세요.
- Git 없이 하려면 전달받은 zip 파일을 풀어서 그 폴더를 쓰면 됩니다.

## 3. 패키지 설치와 설정 파일

**Windows (PowerShell)**

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
copy .env.example .env
```

**macOS · Linux**

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
```

- `python` 명령이 없다고 나오면 Windows에서는 `py -m venv .venv`로 해 보세요.
- `.env`를 열어 `ADMIN_PASSWORD=`에 관리자 비밀번호를 넣으세요. 비워 두면 관리자 화면이 잠깁니다.
- `.env`는 git에 올라가지 않습니다. 비밀번호와 DB 주소는 여기에만 적으세요.

## 4. 실행

### VS Code

1. **파일 → 폴더 열기**로 `Building-cleaner` 폴더를 엽니다.
2. 권장 확장(Python, Python Debugger)을 설치하라는 알림이 뜨면 설치합니다.
3. 명령 팔레트(Ctrl+Shift+P)에서 **Python: Select Interpreter**를 실행해 `.venv`를 고릅니다.
4. 왼쪽 **실행 및 디버그**에서 **웹 창구 실행**을 고르고 F5를 누릅니다.
5. 브라우저에서 `http://127.0.0.1:8000`을 엽니다. 관리자 화면은 `/admin`, 아이디는 `admin`입니다.

실행 구성은 `.vscode/launch.json`에 세 개 있습니다.

| 구성 | 하는 일 |
|---|---|
| 웹 창구 실행 | 사이트를 띄웁니다. 중단점을 쓸 때는 이것을 쓰세요 |
| 웹 창구 실행 (코드 고치면 자동 재시작) | 파일을 저장하면 서버가 다시 시작됩니다. 중단점이 안 걸릴 수 있습니다 |
| 테스트 전체 실행 (pytest) | 테스트 73개를 돌립니다 |

### Visual Studio 2022

1. 시작 창에서 **로컬 폴더 열기(Open a local folder)**로 `Building-cleaner` 폴더를 엽니다.
2. 솔루션 탐색기에서 `run_web.py`를 오른쪽 클릭하고 **시작 항목으로 설정(Set as Startup Item)**을 고릅니다.
3. Python 환경으로 `.venv`를 고릅니다.
4. F5를 누르고 브라우저에서 `http://127.0.0.1:8000`을 엽니다.

- 솔루션(.sln) 파일은 만들지 않았습니다. 폴더 열기 방식으로 씁니다.
- Python 개발 워크로드가 설치돼 있어야 하는지는 문서에서 확인하지 못했습니다. Python 파일이 실행되지 않으면 Visual Studio Installer에서 Python 개발 워크로드를 추가해 보세요.

### 터미널만 쓸 때

```
.venv\Scripts\python run_web.py            (Windows)
.venv/bin/python run_web.py                (macOS · Linux)
```

- 다른 포트: `run_web.py --port 8010`
- 코드 고치면 자동 재시작: `run_web.py --reload`
- 테스트: `.venv\Scripts\python -m pytest`
- 화면 확인용 예시 공동구매 넣기: `.venv\Scripts\python -m app.seed --demo` (운영 DB에는 쓰지 마세요)

## 5. 코드가 아닌 파일은 어디에 있나

| 무엇 | 위치 | 여는 프로그램 |
|---|---|---|
| 한 권으로 읽는 전략 보고서 | `docs/빌딩모아관리_전략보고서_2026-11-10.docx` | Word |
| 재무 모델(60개월) | `tools/financial-model-60m-v4.xlsx` | Excel |
| 전략·브랜딩 요약 | `docs/strategy-report.md`, `docs/brand-strategy.md` | VS Code 미리보기(Ctrl+Shift+V) |
| 마포 대상 건물 6,382동 목록 | `research/market/target_mapo_building_list.csv` | Excel |
| 그 밖의 원자료 | `research/` (설명은 `research/README.md`) | Excel |
| 운영 템플릿, 인터뷰 가이드 | `ops/`, `interview/`, `pilot/`, `service/`, `sourcing/` | VS Code, Excel |

CSV는 UTF-8입니다. Excel에서 한글이 깨지면 **데이터 → 텍스트/CSV에서**로 불러오세요.

## 6. 막힐 때

| 증상 | 해결 |
|---|---|
| `pip install`에서 `psycopg` 오류 | Python 버전을 확인하세요(`python --version`). 3.11–3.14에서 설치 파일이 있는 것을 확인했습니다 |
| 8000번 포트가 이미 쓰이는 중 | `run_web.py --port 8010` |
| 관리자 화면에 못 들어감 | `.env`의 `ADMIN_PASSWORD`를 넣고 서버를 다시 시작하세요 |
| `git clone`에서 로그인 요구 | 비공개 레포라 GitHub 로그인이 필요합니다 |
| 신청 기록이 어디 저장되나 | `data/app.db`(SQLite). `.env`에 `DATABASE_URL`을 넣으면 Supabase를 씁니다 |

## 7. 내 컴퓨터에서 Claude와 이어서 작업하기

클라우드 세션은 대표님 컴퓨터에 접속할 수 없습니다. 컴퓨터에서 이어서 하려면 이 폴더를 연 상태에서 Claude Code(VS Code 확장 또는 데스크톱 앱)를 실행하세요. 지금까지의 결론과 근거는 `docs/`와 `research/`에 있어서 새 세션도 이어받을 수 있습니다.
