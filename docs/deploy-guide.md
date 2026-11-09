# 배포 가이드: 도메인 · GitHub · Supabase · Vercel

> 2026-11-09 기준으로 각 서비스의 공식 문서를 검색해서 확인한 내용입니다. 이 문서를 만든 환경에서는 vercel.com·supabase.com 페이지를 직접 열 수 없어서 **검색 결과에 인용된 공식 문서 내용**을 근거로 했습니다.
> 버튼 이름이나 화면 배치는 바뀔 수 있으니, 다르게 보이면 같은 뜻의 메뉴를 찾으세요. 요금은 각 서비스의 요금 페이지에서 확인하세요.

## 전체 그림

```
건물주 휴대폰 ──▶ buildingmoa.kr (도메인, 등록업체에서 구매)
                      │ DNS
                      ▼
                   Vercel ── GitHub(main 브랜치)에 올라온 코드를 자동으로 배포
                      │ DATABASE_URL
                      ▼
                   Supabase (Postgres, 서울 리전) ── 신청 기록 저장
```

- **GitHub**: 코드 보관소. 이미 `Hollahoe/Building-cleaner`에 있습니다.
- **Vercel**: 사이트를 인터넷에 띄우는 곳. GitHub 저장소와 연결해 두면 `main`에 올라온 코드로 다시 배포합니다(프로젝트 설정의 Git 항목에서 확인).
- **Supabase**: 신청 기록을 저장하는 데이터베이스(Postgres). Vercel 서버는 파일을 계속 보관하지 않기 때문에 DB가 따로 필요합니다.

## 0. 시작 전에: 플랜과 비용

| 서비스 | 무료로 시작 | 영업을 시작하면 |
|---|---|---|
| Vercel | Hobby 플랜으로 테스트 가능 | **Hobby는 비상업적 개인 용도만 허용**됩니다. 서비스를 홍보하거나 돈을 버는 사이트는 Pro 이상이 필요하고, 위반하면 배포가 정지될 수 있습니다. 실제 건물주에게 링크를 보내기 전에 Pro로 바꾸세요. |
| Supabase | Free 플랜으로 시작 가능 (DB 500MB) | Free 플랜은 **1주일 동안 활동이 적으면 프로젝트가 일시 정지**됩니다. 정지되면 사이트에서 신청을 받을 수 없으니, 실제 운영에는 정지되지 않는 유료 플랜을 권장합니다. |
| 도메인 | - | 1년 단위로 결제 |

**권장 순서:** 무료 플랜으로 1–5단계를 끝까지 해 보고 → 문제없으면 공개 직전에 Vercel Pro(필요하면 Supabase 유료 플랜)로 올립니다.

## 1. 이름과 도메인 정하기

1. **상표 확인**: [KIPRIS](https://www.kipris.or.kr)에서 "빌딩모아관리", "빌딩모아"를 검색해 같은 업종(부동산 관리·건물 관리 서비스)에 이미 등록된 상표가 있는지 봅니다. 애매하면 변리사에게 물어보세요.
2. **도메인 후보** (가능 여부는 등록업체에서 검색해야 압니다):
   - `buildingmoa.kr`, `buildingmoa.co.kr`, `buildingmoa.com`
   - `빌딩모아.kr` 같은 한글 도메인도 있지만, 카톡·문자에서 링크가 깨지거나 길게 바뀔 수 있어 영문을 권합니다.
3. **구매**: 국내 도메인 등록업체(예: 가비아, 후이즈 등)에서 구매합니다. 이때 **DNS 설정 화면이 어디 있는지** 확인해 두세요(5단계에서 씁니다).
4. 정한 이름은 Vercel 환경 변수 `BRAND_NAME`에 넣습니다(4단계). 코드는 고칠 필요 없습니다.

## 2. GitHub 정리

1. [PR #1](https://github.com/Hollahoe/Building-cleaner/pull/1)을 검토하고 **Merge** 해서 `main` 브랜치에 넣습니다.
2. 저장소 **Settings → General → Default branch**를 `main`으로 바꿉니다. (지금은 작업 브랜치가 기본으로 되어 있습니다.)
3. 4단계에서 Vercel과 연결하면, 이후 `main`에 들어간 코드로 Vercel이 다시 배포합니다.

## 3. Supabase 만들기

1. [supabase.com](https://supabase.com)에서 GitHub 계정으로 가입합니다.
2. **New project**를 만듭니다.
   - 이름: `buildingmoa`
   - **Database Password**: 길고 무작위로 만들고 비밀번호 관리자에 저장합니다. 4단계에서 씁니다.
   - **Region: Northeast Asia (Seoul)** 를 고릅니다. 건물주와 가까워 빠르고, 데이터가 국내 리전에 있습니다.
3. 프로젝트가 만들어지면 상단의 **Connect** 버튼을 눌러 연결 주소를 봅니다.
   - **Transaction pooler**(포트 **6543**) 주소를 복사합니다. Vercel처럼 요청마다 잠깐 켜지는 서버에는 이 방식이 맞습니다.
   - 주소 안의 `[YOUR-PASSWORD]`를 2번에서 만든 DB 비밀번호로 바꿉니다.
   - 모양: `postgresql://postgres.[프로젝트ID]:[비밀번호]@[호스트].pooler.supabase.com:6543/postgres`
4. **표(테이블)는 만들 필요 없습니다.** 사이트가 처음 켜질 때 필요한 표를 자동으로 만듭니다.

> 참고: 트랜잭션 풀러는 "prepared statement"를 지원하지 않습니다. 이 사이트 코드는 이미 그 기능을 끄고 연결하므로 따로 설정할 것은 없습니다.

## 4. Vercel에 올리기

1. [vercel.com](https://vercel.com)에서 GitHub 계정으로 가입합니다.
2. **Add New → Project**에서 `Hollahoe/Building-cleaner` 저장소를 **Import** 합니다. (저장소가 안 보이면 Vercel GitHub 앱에 이 저장소 접근을 허용하세요.)
3. 프레임워크는 **FastAPI**로 잡힙니다. Vercel은 `app/` 폴더의 `asgi.py` 같은 정해진 파일에서 `app`을 찾아 실행합니다. 이 저장소의 진입점이 바로 `app/asgi.py`입니다.
4. **Environment Variables**에 아래 값을 넣습니다.

| 이름 | 값 | 필수 |
|---|---|---|
| `DATABASE_URL` | 3단계에서 복사한 Transaction pooler 주소 (비밀번호 포함) | 필수 |
| `ADMIN_PASSWORD` | 관리자 화면 비밀번호. 길고 무작위로 | 필수 |
| `COOKIE_SECURE` | `true` | 필수 |
| `BRAND_NAME` | `빌딩모아관리` (1단계에서 확정한 이름) | |
| `SERVICE_AREA` | 집중할 구, 예: `마포구` | |
| `SERVICE_DONGS` | 그 구의 동 목록, 쉼표로 구분 (구청 홈페이지에서 확인) | |
| `DEMAND_THRESHOLD` | 견적을 받기 시작할 건물 수, 기본 `5` | |
| `CONTACT_PHONE`, `CONTACT_EMAIL`, `KAKAO_URL` | 연락처, 카카오톡 채널 채팅 링크 | |
| `BUSINESS_INFO`, `PRIVACY_OFFICER` | 사업자등록 후 상호·대표·등록번호, 개인정보 보호 책임자 | 공개 전 |

5. **Deploy**를 누릅니다. 끝나면 `https://프로젝트이름.vercel.app` 주소가 생깁니다.
6. 확인:
   - `https://…vercel.app/healthz` → `ok`가 나오면 서버가 켜진 것입니다.
   - 첫 화면 → "우리 동네 공동구매 신청"으로 테스트 신청을 하나 넣습니다.
   - `/admin` → 아이디 `admin`, 4번의 비밀번호로 들어가 신청이 보이는지 확인한 뒤, 테스트 신청은 상태를 '취소'로 바꿉니다.
   - Supabase의 **Table Editor**에서 `demands` 표에 줄이 생겼는지 봅니다.

> `DATABASE_URL` 없이 Vercel에서 실행하면, 사이트가 일부러 시작하지 않고 "DATABASE_URL을 넣어야 합니다"라는 오류를 냅니다. Vercel 서버의 파일은 남지 않아 신청 기록이 사라지기 때문입니다.

## 5. 도메인 연결

1. Vercel 프로젝트 **Settings → Domains**에 `buildingmoa.kr`과 `www.buildingmoa.kr`을 추가합니다.
2. Vercel이 보여 주는 값대로 도메인 등록업체의 DNS 설정에 레코드를 넣습니다.

| 이름(호스트) | 종류 | 값 |
|---|---|---|
| `@` (도메인 그대로) | **A** | Vercel 도메인 카드에 나온 IP. 많은 프로젝트에서 `76.76.21.21`이지만 **반드시 내 프로젝트 화면의 값을 쓰세요** |
| `www` | **CNAME** | Vercel 도메인 카드에 나온 값(프로젝트마다 다름) |

   - 등록업체에 원래 있던 `@`의 A 레코드(주차 페이지 등)는 **지웁니다**. 남아 있으면 연결 확인이 실패합니다.
   - 다른 방법: 도메인의 네임서버를 `ns1.vercel-dns.com`, `ns2.vercel-dns.com`으로 바꾸면 Vercel이 DNS를 직접 관리합니다.
   - Cloudflare를 쓰는 경우 해당 레코드를 프록시 끔(DNS only)으로 두세요.
3. 반영까지 몇 분에서 몇 시간 걸릴 수 있습니다. Vercel 도메인 화면에 연결 완료 표시가 뜨면 `https://buildingmoa.kr`로 열리는지, 주소창에 자물쇠가 보이는지 확인하세요.

## 6. 공개 전 점검표

- [ ] Vercel **Pro**로 변경 (상업적 사용)
- [ ] Supabase 프로젝트가 정지되지 않는 플랜인지 확인
- [ ] `ADMIN_PASSWORD`는 다른 곳에서 쓰지 않는 긴 비밀번호
- [ ] `COOKIE_SECURE=true`
- [ ] 개인정보처리방침(`/privacy`)의 책임자·연락처를 채우고, 문구를 전문가에게 1회 검토
- [ ] 꼬리말 사업자 정보 채우기 (사업자등록 후)
- [ ] 테스트 신청은 관리자 화면에서 '취소' 처리
- [ ] 주 1회 관리자 화면에서 CSV 3종(공동구매 신청, 협력 업체, 진단 신청)을 내려받아 보관
- [ ] 카톡 프로필, 명함, 전단에 도메인 넣기

## 7. 문제가 생기면

| 증상 | 확인할 것 |
|---|---|
| Vercel 배포 로그에 "DATABASE_URL" 오류 | 4단계 환경 변수에 `DATABASE_URL`을 넣고 다시 배포 |
| 사이트가 "Internal Server Error" | Vercel 프로젝트의 **Logs**에서 오류 확인. DB 주소의 비밀번호, 포트(6543)가 맞는지 |
| 갑자기 신청이 안 됨, DB 연결 실패 | Supabase 프로젝트가 정지(paused)됐는지 대시보드에서 확인하고 복구 |
| Vercel이 앱을 못 찾음 | 진입점은 `app/asgi.py`의 `app`입니다. Vercel FastAPI 문서의 entrypoint 설정 방법으로 직접 지정하세요 |
| 도메인이 연결 안 됨 | 예전 A 레코드를 지웠는지, Vercel 화면의 값과 정확히 같은지 |

## 다른 방법: Docker + 디스크

Vercel·Supabase 대신, Docker를 돌리고 **재시작해도 지워지지 않는 디스크**를 붙일 수 있는 호스팅(Render, Fly.io, Railway, 일반 VPS 등)에 올려도 됩니다. 이때는 `DATABASE_URL` 없이 SQLite 파일(`/data/app.db`)을 씁니다. 저장소의 `Dockerfile`을 쓰면 되지만, 이 환경에는 Docker가 없어 빌드를 직접 해 보지는 못했습니다.

## 출처 (검색으로 확인한 공식 문서)

- Vercel FastAPI 배포와 진입점 탐색: [Deploy a FastAPI app on Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Zero-configuration FastAPI backends](https://vercel.com/changelog/zero-config-fastapi-backends)
- Vercel 상업적 사용: [Fair Use Guidelines](https://vercel.com/docs/limits/fair-use-guidelines), [Hobby Plan](https://vercel.com/docs/plans/hobby)
- Vercel 도메인 연결: [Setting up a custom domain](https://vercel.com/docs/domains/set-up-custom-domain), [Adding & Configuring a Custom Domain](https://vercel.com/docs/domains/working-with-domains/add-a-domain)
- Vercel 시스템 환경 변수(`VERCEL`): [System environment variables](https://vercel.com/docs/environment-variables/system-environment-variables)
- Supabase 무료 플랜과 정지: [Pricing](https://supabase.com/pricing), [Free Postgres for side projects FAQ](https://supabase.com/kb/faqs/platform/free-postgres-for-side-projects)
- Supabase 서울 리전: [Available regions](https://supabase.com/docs/guides/platform/regions)
- Supabase 연결 방식과 prepared statement: [Connect to your database](https://supabase.com/docs/guides/database/connecting-to-postgres), [Disabling prepared statements](https://supabase.com/docs/guides/troubleshooting/disabling-prepared-statements-qL8lEL)
- psycopg의 prepared statement 끄기: [psycopg Prepared statements](https://www.psycopg.org/psycopg3/docs/advanced/prepare.html)
