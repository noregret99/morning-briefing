# ☀️ 아침 브리핑

매일 아침 카카오톡 "나에게 보내기"로 오늘의 날씨와 주요 뉴스를 AI 3줄 요약으로 받는 프로그램.

## 진행 상황
- [x] 1단계: 파이썬 준비
- [x] 2단계: 카카오 앱 등록 + 테스트 메시지
- [x] 3단계: 날씨 (김해, Open-Meteo)
- [x] 4단계: 뉴스 (구글 뉴스 RSS — 주요 + 경제, 메시지 2개로 나눠 전송)
- [x] 5단계: GitHub Actions로 매일 자동 실행 + 토큰 자동 갱신 + 요약 페이지
  - 실행 설정: `.github/workflows/briefing.yml` (매일 07:00 KST, GitHub 사정으로 몇 분~수십 분 늦을 수 있음)
  - 지금 바로 실행: 저장소 [Actions] → [아침 브리핑] → [Run workflow]
  - 요약 페이지: https://noregret99.github.io/morning-briefing/
  - 금고(Secrets): `KAKAO_REST_API_KEY`, `KAKAO_CLIENT_SECRET`, `KAKAO_REFRESH_TOKEN`, `GH_PAT`, `ANTHROPIC_API_KEY`
  - ⚠️ `GH_PAT`는 "만료 없음"으로 만듦 → 프로젝트를 그만두면 GitHub [Developer settings]에서 꼭 삭제
  - 실패하면 GitHub이 가입 이메일로 알림을 보냄
- [x] 추가: AI 3줄 요약 (2026-11-03, `summarize.py`, Claude `claude-haiku-5-5`)
  - 카톡 = 인사말 + AI 3줄 요약 (메시지 1개), 요약 페이지 맨 위에 🤖 AI 요약 칸
  - 비용: 1회 약 $0.00056 (한 달 약 25원). 크레딧은 **console.anthropic.com**에서 충전 (claude.ai 결제와 별개 지갑!)

## 파일별 역할
| 파일 | 하는 일 |
|---|---|
| `briefing.py` | **메인.** 날씨·뉴스 수집 → AI 3줄 요약 → 카톡 메시지 1개(인사 + AI 요약) 전송 + 요약 페이지 생성. **AI 실패 시 예전 방식**(메시지 1: 날씨 + 주요 뉴스, 메시지 2: 경제 뉴스)으로 자동 대체 |
| `weather.py` | 김해 날씨 가져오기 (Open-Meteo, 키 필요 없음) |
| `news.py` | 구글 뉴스 RSS에서 주요·경제 헤드라인(제목·링크·언론사·설명) 10개씩 가져오기 (키 필요 없음). 설명 = 같은 사건을 다룬 다른 언론사 제목 최대 3개 (기사 본문 아님, AI 요약 참고용). 카톡용은 45자 넘으면 자르고 200자 안에 들어가는 만큼만 담음 |
| `summarize.py` | 날씨·뉴스(+관련 보도)를 Claude(`claude-haiku-5-5`)에 보내 3줄 브리핑(155자 이하)을 받음. 규칙에 안 맞으면 "줄여줘"로 1번 재시도, 그래도 안 되면 오류 → 기존 방식으로 대체. 1회 약 $0.0006. 단독 테스트: `python summarize.py` (카톡 전송 안 함). 🔒 `ANTHROPIC_API_KEY` 필요 |
| `page.py` | 카톡 [자세히 보기]가 열 요약 페이지 `site/index.html` 생성 (맨 위 🤖 AI 요약 칸 + 뉴스 전체 + 원문 링크. AI 실패 시 AI 칸 생략). ⚠️ 공개 페이지라 개인 정보 금지 |
| `kakao_send.py` | 토큰을 새로 받은 뒤 카톡 전송 |
| `kakao_auth.py` | **처음 한 번만.** 카카오 로그인 → 토큰을 `kakao_token.json`에 저장 |
| `.env` | 🔒 비밀: 카카오 REST API 키, 클라이언트 시크릿, Claude API 키 (GitHub에 안 올라감) |
| `requirements.txt` | GitHub 컴퓨터가 설치할 도구 목록 (새 도구를 쓰면 여기에도 꼭 추가!) |
| `kakao_token.json` | 🔒 비밀: 카카오 토큰 (GitHub에 안 올라감) |
| `.gitignore` | GitHub에 올리면 안 되는 파일 목록 |

## 실행 방법
```
python briefing.py --dry-run   # 미리보기 (카톡 전송 안 함)
python briefing.py             # 실제 전송
```

## 🔧 고장 났을 때 확인 순서
1. `python weather.py` → 날씨 글이 나오면 날씨는 정상
2. `python news.py` → 뉴스 제목이 나오면 뉴스는 정상
3. `python summarize.py` → 3줄 요약이 나오면 AI는 정상
4. `python kakao_send.py` → 테스트 메시지가 오면 카톡은 정상
5. 모두 정상이면 `python briefing.py --dry-run` 으로 조립 부분 확인
6. "토큰 갱신 실패"가 나오면 → `python kakao_auth.py` 다시 실행 (리프레시 토큰은 약 2개월 유효)

카톡 인사말에 **"⚠️AI요약 실패"**가 보이면 (GitHub [Actions] 실행 기록에서 원인 확인):
- `credit balance is too low` → console.anthropic.com 에서 크레딧 충전
- `authentication_error` / `invalid x-api-key` → API 키 확인 (.env, 금고 `ANTHROPIC_API_KEY`)
- `Could not resolve authentication method` → 금고나 자동 실행 설정에 키가 연결 안 됨
- `규칙에 맞는 요약을 못 받았어요` → AI가 너무 길게 씀. 하루 이틀 계속되면 `summarize.py` 지시문 조정

자주 나오는 카카오 오류:
- `KOE006`: 리다이렉트 URI 불일치 → 카카오 개발자 사이트에 `http://localhost:5000/callback` 정확히 등록됐는지 확인
- `-402`: 메시지 전송 동의 안 됨 → `kakao_auth.py` 다시 실행해 동의
- `-3`: 동의항목 "카카오톡 메시지 전송" 설정 안 됨

## 실패 대비
- 날씨나 뉴스 하나가 실패해도 나머지는 보내고 "⚠️ 못 가져왔어요"라고 표시
- AI 요약이 실패하면 예전 방식(메시지 2개)으로 보내고, 인사말 줄에 "⚠️AI요약 실패" 표시
- 카톡 전송 자체가 실패하면 프로그램이 오류로 끝남 → (5단계) GitHub이 실패 메일 발송
- 모든 실행 기록은 `[시:분:초]`와 함께 화면(로그)에 남음

## 📏 작업 원칙 (AI와 작업할 때도 이 순서로)
1. **기획**: 무엇을 왜 할지 먼저 정하고, 한 단계씩만 진행
2. **미리 출력**: 진짜 실행 전에 화면으로 결과 확인 (`--dry-run`)
3. **검증**: 입력값 확인 (비밀 키는 값이 아니라 길이·형식만 확인)
4. **테스트**: 만들자마자 실행, 실패 상황도 일부러 흉내 내서 확인
5. **저장 지점**: 잘 되면 Git 커밋 (비밀 파일이 빠졌는지 확인 후)
6. **실패 알림**: 조용히 실패하지 않게
7. **설명서**: 이 README를 계속 최신으로 유지

## 참고
- 카톡 기본 텍스트 메시지는 **최대 200자**
- 메시지 버튼 링크는 카카오 개발자 사이트 [제품 링크 관리] > [웹 도메인]에 등록된 주소만 가능
  - 환경변수 `BRIEFING_PAGE_URL`(요약 페이지 주소)이 있으면 그 주소, 없으면 `https://www.naver.com`
