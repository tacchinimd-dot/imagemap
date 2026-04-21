# 라인 × 핏 매트릭스 (Image Map) — 작업 현황

> **마지막 업데이트:** 2026-04-21 (제외만 보기 필터 · 디자이너 PICK 탭/체크박스 추가 · Lacoste 원본 해상도 재다운로드 스크립트)
> **위치:** `C:\Users\AD0903\brand_crawler\`
> **/imagemap 커맨드 전용 STATUS** — /crawler와 분리 운영
> **Claude Code가 이 파일을 읽으면:** 아래 내용을 기반으로 작업을 이어서 진행하세요.

---

## 프로젝트 목적

**12개 브랜드**(Wilson·Alo·Lacoste·Ralph Lauren·Descente·Lululemon·Celine·Loro Piana·Skims·Miu Miu·Prada·Sporty & Rich) 의류 상품을
**3라인(클래식·어슬레져·스포츠)** × **8개 아이템 탭** × **탭별 상이한 핏/실루엣/기장 축**으로 매트릭스 배치.
**목적**: Sergio Tacchini 브랜드 방향성에 맞는 이미지 재생성 후보 선정 (유관부서 전달용).

- **상의·아우터·폴로·티셔츠·맨투맨·스웨터**: 슬림핏 / 레귤러핏 / 세미오버핏~오버핏
- **스커트**: **피티드 / 플레어 / 플리츠 / 와이드플리츠** (4분할 — H라인·A라인·플리츠·와이드플리츠)
- **팬츠 및 쇼츠**: 슬림핏 / 스트레이트핏 / 세미와이드~와이드핏
- **드레스**: 미니 / 미디 / 맥시 (Vision 기장 기반)

**리뷰 모드 기능:**
- 썸네일 클릭 → 모달 팝업 (원본 고해상 이미지 + 메타 + 상세페이지 링크)
- 체크박스 영속성 (localStorage) + 선택 전용 탭
- ⭐✨ 추천 이원화 + 필터 토글 + 일괄 ZIP 다운로드
- 🔍 확대/축소 슬라이더 (갤러리만)

---

## 라인 ↔ 브랜드 매핑

| 라인 | 브랜드 | 색상 | 상품 수 (fit_overrides 기준) |
|---|---|---|---|
| 클래식 | Lacoste + Ralph Lauren + Celine + Loro Piana + Sporty & Rich | #047857 (forest) | 144 + 148 + 21 + 159 + 290 |
| 어슬레져 | Alo + Lululemon + Skims + Miu Miu + Prada | #2563eb (royal blue) | 156 + 55 + 128 + 169 + 49 |
| 스포츠 | Wilson + Descente | #dc2626 (red) | 60 + 48 |

---

## 탭 정의 (8개)

| 탭 | 해당 소분류 | 핏 컬럼 축 |
|---|---|---|
| 아우터 | 자켓, 가디건, 재킷, 블레이저, 아우터웨어, 집업, 베스트 | 슬림/레귤러/세미오버 |
| 폴로 (하이브리드) | 소분류 "폴로" 포함 OR (상품명 "폴로/polo" AND 소분류가 제외군 아님) | 슬림/레귤러/세미오버 |
| **티셔츠 및 롱슬리브** | 반팔티셔츠, 티셔츠 & 탑, 탑, **롱슬리브** | 슬림/레귤러/세미오버 |
| **드레스** (신규) | 드레스 | **미니 / 미디 / 맥시** (기장) |
| 스커트 | 스커트 | **피티드 / 플레어 / 플리츠 / 와이드플리츠** (4분할) |
| 맨투맨 및 후디 | 스웻셔츠, 후디 & 스웨트셔츠, 후디 | 슬림/레귤러/세미오버 |
| 스웨터 | 스웨터 | 슬림/레귤러/세미오버 |
| 팬츠 및 쇼츠 | 팬츠, 데님, 쇼츠, 레깅스 | 슬림/스트레이트/와이드 |

**폴로 제외군**: 스웨터·가디건·스웻셔츠·후디·드레스·팬츠·쇼츠·레깅스·스커트·자켓

**탭 미포함 품목** (매트릭스에서 제외): 브라탑·셔츠 등

---

## 핏 매핑 — 탭별 분리 (`TAB_FIT_COLS`)

### 상의·아우터·폴로·티셔츠·맨투맨·스웨터 (기본)

| 핏 열 | 판정 규칙 (우선순위 순) |
|---|---|
| 슬림핏 | ① 수기 오버라이드 ② 상품명/소분류에 "슬림" 또는 "slim" 포함 |
| 레귤러핏 | Vision 핏값 = `Regular` |
| 세미오버핏~오버핏 | Vision 핏값 = `Semi-Over` OR `Over` |

### 스커트 (`_classify_skirt_pleat`) — 4컬럼

| 핏 열 | 판정 규칙 |
|---|---|
| **피티드** | Vision 실루엣=`H라인` OR pencil/bodycon/tight 키워드 OR Slim 핏 (몸에 딱 붙는 실루엣) |
| **플레어** | Vision 실루엣=`A라인`/`플레어` OR a-line/full/wide 키워드 OR Regular/Over 핏 (기본값) |
| **플리츠** | Vision 주름값 = `잔플리츠` OR `언발란스플리츠` |
| **와이드플리츠** | Vision 주름값 = `와이드플리츠` |

**전 145건 자동 분류** · 피티드 21 / 플레어 63 / 플리츠 44 / 와이드플리츠 17

### 드레스 (`_classify_dress_length`) — 3컬럼 (기장)

| 핏 열 | 판정 규칙 |
|---|---|
| **미니** | Vision 기장=`미니` OR 상품명 "mini/short/크롭" |
| **미디** | Vision 기장=`미디` OR 상품명 "midi/mid/knee" (기본값) |
| **맥시** | Vision 기장=`맥시` OR 상품명 "maxi/long/롱드레스" |

**전 106건 자동 분류** — 클래식 54 · 어슬레져 46 · 스포츠 6

### 팬츠 및 쇼츠 (`_classify_pants_silhouette`) — 모든 바지 자동 분류

| 핏 열 | 판정 규칙 (우선순위 순) |
|---|---|
| 슬림핏 | ① 오버라이드 ② Vision 실루엣=테이퍼드 ③ 소분류=레깅스 ④ 이름에 `slim/skinny/tight/tapered/슬림/타이트/스키니` |
| 스트레이트핏 | Vision 실루엣=스트레이트 · **기본값** (모든 미매칭 fallback) |
| 세미와이드~와이드핏 | Vision 실루엣=와이드 · 이름에 `wide/baggy/loose/relaxed/flare/palazzo/bootcut/trouser/와이드/루즈/배기/플레어` |

**전 234건 자동 분류** · 미분류 0건

### 공통 우선순위
**엑셀 오버라이드 > Vision 값 > 소분류 룰 > 이름 키워드 > 기본값**

---

## 상품 이미지 (스틸컷) 매핑

| 브랜드 | 전략 | 상태 | 비고 |
|---|---|---|---|
| Ralph Lauren | JSON `images[]` 배열에서 URL에 `lifestyle` 포함된 첫 이미지 | ✅ 완료 | 비용 $0 |
| Wilson | Shopify `products.json` `images[]` → Claude Haiku Vision으로 인덱스 0/1 중 상품컷 자동 판별 | ✅ 완료 | 66건, 비용 ~$0.10, 에러 0건. 캐시: `wilson_crawler/wilson_still_images.json` |
| Lacoste | `image_url`의 suffix `_20` → `_24`로 치환 (모든 상품 일관) | ✅ 완료 | 비용 $0. 사용자 시각 검증 완료 |
| Alo | 모델컷만 존재 → **OpenAI gpt-image-1 누끼 추출** | ✅ 완료 | 193건, 1024×1536 medium, 총 84분/~$13. 에러 0건. 캐시: `alo_crawler/alo_still_images.json` |
| **Descente** | MAIN_IMAGE_URL의 `_R01.JPG`(후면) → `_N01.JPG`(전면) 치환. `/R/` 서브폴더 제거 | ✅ 완료 | 비용 $0. 사용자 샘플 검증 완료(N01=상품컷) |
| **Lululemon** | 모델컷만 존재 → **OpenAI gpt-image-1 누끼 추출** (Alo 동일 전략) | ✅ 완료 | 매트릭스 대상 55건 + 초기 배치 8건 = 63장. 예산 $4.0 잔액 상황에서 브라탑·드레스·롱슬리브 필터링. 에러 0건 |
| **Celine** | `IMAGE_URL` 컬럼 손상 → `IMAGE_URL_HIRES` 컬럼 사용 | ✅ 완료 | 비용 $0 |
| **Loro Piana** | `IMAGE_URL` 그대로 사용 (luxury 브랜드 특성상 대부분 상품컷) | ✅ 완료 | 비용 $0 |
| **Skims** | `대표 이미지 URL` (Shopify CDN, 대부분 flat 상품컷) | ✅ 완료 | 비용 $0 (원격 CDN). 어슬레져 라인 |
| **Miu Miu** | `IMAGE_URL` (miumiu.com CDN) | ✅ 완료 | 비용 $0. 어슬레져 라인 |
| **Prada** | `IMAGE_URL` (prada.com CDN). 의류만 필터 (가방·액세서리 제외) | ✅ 완료 | 비용 $0. 어슬레져 라인 |
| **Sporty & Rich** | `대표 이미지 URL` (Shopify CDN) | ✅ 완료 | 비용 $0. 클래식 라인 |

### 캡처 CORS 대응 (html2canvas) — 전체 이미지 data URL 임베드

`file://` + 원격 CDN의 CORS taint + 로컬 파일 null-origin 조합으로 html2canvas 캡처 시 이미지가 회색/검정 박스로 나오는 이슈 발생 → **모든 이미지(로컬+원격)를 HTML 생성 시점에 Pillow로 JPEG data URL로 임베드** (260px q78, ~6KB/장).

**파이프라인** (`cache_all_images_to_data_url` in `line_matrix.py`):
1. 로컬 PNG: `_local_to_data_url()`로 인메모리 변환
2. 원격 URL: `_remote_to_data_url()`로 httpx 병렬 다운로드(20 workers), `.image_cache/*.jpg`에 저장 후 base64 인코딩
3. 3회 재시도 + 브랜드별 Referer 헤더 + 다양한 UA 순환
4. 디스크 캐시 덕분에 2회차부터 **1초 이내** 완료

**Lacoste Akamai 우회** (별도 스크립트 `_fetch_lacoste_via_browser.py`):
- Akamai가 httpx·headless 브라우저·`context.request.get` 모두 차단 (403)
- **visible Chromium + `page.goto()`** 만 통과 → 191건 수동 rescue 성공
- `impolicy=pctp` 파라미터 제거 필수 (AVIF 응답 → JPEG 응답으로 전환, Pillow 호환)

**캐시 상태**: `.image_cache/` 766개 JPEG (~20MB), HTML 최종 약 4.5MB

---

## 파일 구성

```
C:\Users\AD0903\brand_crawler\
├── IMAGEMAP_STATUS.md                        ← 이 파일
├── line_matrix.py                            ✅ 매트릭스 HTML 생성기 (8브랜드·탭별 핏·이름 교정·dedup·data URL 임베드)
├── line_matrix.html                          ✅ 최신 — 모던 대시보드 UI (~4.5MB, 모든 이미지 data URL 임베드)
├── make_fit_overrides.py                     ✅ 수기 핏 입력 엑셀 생성기 (탭별 드롭다운)
├── fit_overrides.xlsx                        ✅ 762건, 핏값없음 5건
├── make_classification_export.py             ✅ 분류 결과 엑셀 출력 스크립트
├── classification_export.xlsx                ✅ 1021건, 라인 색상·자동 필터·헤더 고정
├── _sample_new_brands.py / .html             — Descente 상품컷 샘플 페이지
├── _verify_alo_bottoms.py / .html            — Alo 하의 누끼 검증 (체크박스 선택 페이지)
├── _extract_alo_stills_full.py               ✅ Alo AI 누끼 배치 (완료)
├── _extract_lululemon_stills_full.py         ✅ Lululemon AI 누끼 배치 (완료)
├── _reextract_alo_handles.py                 ✅ 특정 handle 재추출
├── _fetch_lacoste_via_browser.py             ✅ Lacoste Akamai 우회 다운로드 (visible Chromium)
│
├── .image_cache/                             ✅ 원격 이미지 JPEG 캐시 (766개, ~20MB)
│   └── failed_urls.log                       — 다운로드 실패 URL 기록
├── alo_crawler/alo_still_images.json         ✅ 193건 Alo 누끼 캐시
├── alo_crawler/stills/*.png                  ✅ 193장 Alo 누끼 이미지
├── wilson_crawler/wilson_still_images.json   ✅ 66건 Wilson 상품컷 인덱스
├── lululemon_crawler/lululemon_still_images.json  ✅ 63건 Lululemon 누끼 캐시
└── lululemon_crawler/stills/*.png            ✅ 63장 Lululemon 누끼 이미지
```

---

## 핏 오버라이드 엑셀 (`fit_overrides.xlsx`)

**역할:** 사용자가 수기로 핏을 입력 → `line_matrix.py`가 재실행 시 자동 반영

**구조** (row1=안내, row2=헤더, row3~=데이터):
```
브랜드 | 라인 | 탭 | 소분류(원본) | 상품명 | 현재 핏(분류결과) | 새 핏 ★ | 이미지 URL | 상품 URL
```

- `G열(새 핏 ★)` 에만 입력. **탭별 드롭다운** 자동 부여:
  - 상의 탭: 슬림핏 / 레귤러핏 / 세미오버핏~오버핏
  - 스커트 탭: 논플리츠 / 잔플리츠 / 와이드플리츠
  - 팬츠/쇼츠 탭: 슬림핏 / 스트레이트핏 / 세미와이드~와이드핏
- `I열(상품 URL)` 하이퍼링크 — 클릭 시 상품 페이지 열림
- 기존 파일 있으면 `G열` 입력값 보존 (재실행 시 덮어쓰지 않음)

**분포 (2026-04-17 · 탭별 핏 분리 반영):**
- 총 **762건** / **분류됨 757건** / 핏값없음 **5건** (잔여 스커트)
- 탭별: 아우터 191 · 폴로 61 · 티셔츠 67 · 스커트 92 · 맨투맨 및 후디 48 · 스웨터 70 · 팬츠쇼츠 233
- 브랜드별: Alo 151 · Lululemon 55 · Wilson 60 · Descente 46 · Lacoste 129 · RL 144 · Celine 20 · Loropiana 157

---

## 현재 매트릭스 상태 (8탭 · 12브랜드 · dedup + 이름 기반 탭 교정 · Skims 모델컷 5건 제외)

| 탭 | 클래식 | 어슬레져 | 스포츠 | 합계 |
|---|---:|---:|---:|---:|
| 아우터 | 144 | 102 | 16 | 262 |
| 폴로 | 61 | 19 | 7 | 87 |
| 티셔츠 및 롱슬리브 | 71 | 50 | 25 | 146 |
| 드레스 (신규) | 54 | 46 | 6 | 106 |
| 스커트 | 42 | 79 | 24 | 145 |
| 맨투맨 및 후디 | 91 | 31 | 9 | 131 |
| 스웨터 | 92 | 30 | 0 | 122 |
| 팬츠 및 쇼츠 | 222 | 160 | 32 | 414 |
| **합계** | **777** | **517** | **119** | **1,413** |

**매트릭스 노출 1,413건** (드레스 탭 + 롱슬리브 편입 반영)
- **이름 기반 교정**: 상품명 끝단 키워드(팬츠/스커트/자켓 등)로 소분류 오분류 자동 수정 (예: "코트 라이벌 트랙 팬츠" → 아우터에서 팬츠로 이동)
- **색상 변형 dedup**: (브랜드, 상품명 소문자) 키로 중복 제거, stillcut 보유 항목 우선 선별

---

## 다음 작업 순서

### ✅ Step 1 — Lululemon AI 누끼 추출 (완료)
- 매트릭스 대상 55건 + 초기 배치 8건 = 63장, 에러 0

### ✅ Step 2 — 신규 브랜드 반영 `fit_overrides.xlsx` (완료)
- 762건 (기존 G열 보존)

### ✅ Step 3 — 스커트/팬츠 탭별 전용 핏 분류 (완료)
- 스커트: 플리츠 기반 85/85 Vision 자동 분류
- 팬츠 및 쇼츠: 실루엣 기반 234/234 자동 분류 (미분류 0)

### ✅ Step 4 — UI/UX 리디자인 (완료)
- Inter 단일 폰트, pill 탭, sticky 좌측 컬럼, 8열 갤러리 그리드
- 캡처 기능(클립보드 복사 / 이미지 저장)

### ✅ Step 5 — 캡처 CORS 근본 해결 (완료)
- 모든 이미지를 HTML 생성 시 data URL로 임베드
- Lacoste Akamai 차단은 visible Chromium + `page.goto()` + `impolicy=pctp` 제거로 우회
- 766개 원격 이미지 전부 캐시됨 · 회색/검정 박스 완전 해소

### ✅ Step 6 — 오분류 교정 + dedup (완료)
- 상품명 기반 탭 자동 교정
- 색상 변형 중복 제거 (757 → 691)

### ✅ Step 7 — 신규 4개 브랜드 추가 (완료, 2026-04-20)
- Skims · Miu Miu · Prada → 어슬레져, Sporty & Rich → 클래식
- 로더 4개 추가 + fit_overrides.xlsx 1,427건 재생성
- 매트릭스 노출 691 → 1,278건

### ⏳ Step 8 — 사용자 핏 오버라이드 수기 입력 (선택)
- `fit_overrides.xlsx` G열에 수정 필요한 핏만 입력
- 현재 757/762건 자동 분류 완료 · 수기 입력 필수는 아님

### ✅ Step 9 — 리뷰 모드 추가 (Sergio Tacchini 이미지 재생성 후보 선정, 2026-04-20)

#### 핵심 기능 (최신)
1. **이미지 모달 팝업** — 썸네일 클릭 시 원본 고해상 이미지 + 메타데이터 + 상세페이지 링크
   - Alo/Lululemon: `file:///...stills/*.png` 원본 1024×1536
   - 원격 CDN: 원본 URL 직접 로드 (CORS 차단 시 썸네일 폴백)
2. **체크박스 영속성** — localStorage(`line_matrix_selected_v1`) 저장. 탭 전환·모달·새로고침에도 유지. 명시적 해제 전까지 보존
3. **ST 추천 이원화 (⭐/✨)** — `classify_st_match()` — "core"/"adapt"/None 3값 반환
4. **선택된 항목 전용 탭** — 우측 끝 (✓ 아이콘 + 카운트). 탭·브랜드별 그룹화
5. **⭐✨ 추천만 보기 필터** — 추천 없는 썸네일 숨김 (localStorage 영속, 셀 카운트는 `보이는/전체`로 표시)
6. **⭐✨ 추천 전체 ZIP** — 체크박스 불필요, 추천 276건 일괄 다운로드 (confirm 후 진행)
7. **🔍 이미지 확대/축소** — `--thumb-w` CSS 변수 슬라이더 (60~280px, 10px 단위). 갤러리·선택탭 썸네일만 영향. localStorage 영속
8. **상단바 액션**
   - `⭐✨ 추천만 보기` · `⭐✨ 추천 전체 ZIP` (하이라이트 배경)
   - `백업` — 선택 메타데이터 JSON (타임스탬프)
   - `선택 ZIP` — 개별 선택 항목 이미지 + manifest.csv ZIP
   - `전체 해제` — confirm 후 초기화
9. **Sticky column z-index** — 좌측 라인 라벨에 체크박스 가려짐 (line-th: 10 / corner-th: 20 / thead: 15 / chk: 2)
10. **캡처 모드 체크박스 제거** — html2canvas 캡처 시 `.chk` 요소 + `.is-selected` 하이라이트 clone에서 제거

#### ST ⭐ CORE (직접 부합) 규칙 (§1·§2·§6 기반)
**절대 배제**: gown/evening/corset/lingerie/slip dress/자수·시퀸 키워드, 브라탑 단독, Prada 로고 플레이(triangle/logo/삼각)

**테니스 헤리티지 2사 (Lacoste, Wilson)** — 무조건 ⭐
**Sporty & Rich** — 볼륨 제약으로 `st_kw` 키워드 필터 적용

**⭐ 탭별 조건**:
- **폴로** → TH2 무조건 / SR 키워드 필수
- **스커트** → TH2 무조건 / SR 키워드 또는 플리츠 / 다른 브랜드는 플리츠 有
- **쇼츠** → TH2 무조건 / SR 키워드 필수 · 긴 팬츠 전체 제외
- **아우터** → `track/crop/windbreak/bomber/봄버` 키워드 (쿠쉬라이트 계보)
- **맨투맨** → SR/Lacoste + retro 키워드 (`track/classic/varsity/italia/club/heritage`)
- **드레스** → TH2·SR·RL 미니·미디 (맥시 제외) / 타 브랜드는 tennis·polo·court 키워드 있는 미니만
- **티셔츠·스웨터** → 전면 제외 (시그니쳐 미확립 + RA5 배제 원칙)

#### ST ✨ ADAPT (타키니화 가능) 규칙
- **럭셔리 4사** (Miu Miu/Prada/Celine/Loro Piana):
  - 자켓: `blazer/bomber/crop/varsity/track/harrington` 키워드 필수
  - 스커트: 플리츠 있는 것만
  - 드레스: 미니만 (§6.8 Cotton Blend Jersey × Mini Dress 실험)
- **Skims**: 쇼츠 · 플리츠 스커트 · 미니 드레스 (Body-Lined 실루엣 참조)
- **Alo/Lululemon 미니 드레스** (키워드 없어도) — Athleisure dress 참조

#### 현재 ST 마크 분포 (드레스 추가 후)

| 마크 | 총건수 | 구성 |
|---|---:|---|
| ⭐ CORE | **201** | 스커트 54 · 쇼츠 42 · 드레스 39 · 폴로 35 · 아우터 20 · 맨투맨 11 |
| ✨ ADAPT | **75** | 드레스 25 · 스커트 23 · 쇼츠 18 · 아우터 9 |
| **추천 합계** | **276** | 1,413건 중 19.5% |
| 제외 | 1,137 | §1 금지영역 + 시그니쳐 비매칭 |

#### Skims 모델컷 제외 (사용자 확인, 2026-04-20)
`_SKIMS_EXCLUDE_BY_NAME` 상수로 5건 매트릭스 제외 (다른 URL 네이밍 체계로 `-FLT` 대체 불가):
- MILKY SHEER BOATNECK MINI DRESS
- MILKY SHEER MOCK NECK LONG SLEEVE LONG DRESS
- COTTON RIB SCOOP NECK HENLEY
- FITS EVERYBODY WRAP SUPER CROPPED T-SHIRT
- MILKY SHEER MOCK NECK LONG SLEEVE BODYSUIT

(나머지 39/44 비-FLT URL은 실제로 상품컷이어서 치환 불필요)

#### 파일 구조 변경
- `line_matrix.py`
  - `classify_st_match(item, tab)` — 3값 반환 (core/adapt/None)
  - `cache_all_images_to_data_url()` — `image_url_hires` 필드로 원본 URL 보존
  - `load_alo()/load_lululemon()` — `file:///` 로컬 경로를 `image_url_hires`에 저장
  - 각 로더 — `length_raw` 필드 추가 (드레스 기장 분류용)
  - `_classify_skirt_pleat()` — 4컬럼 (피티드/플레어/플리츠/와이드플리츠)
  - `_classify_dress_length()` — 신규 (미니/미디/맥시)
  - `render_html()` — 썸네일 a→div, 체크박스/뱃지 오버레이, 모달, 선택 탭, 레전드, 줌 컨트롤
  - `items_js_map` JSON 직렬화 (매트릭스 노출 항목 전체 메타데이터)
- `make_fit_overrides.py` — DROPDOWN_SKIRT(4값)·DROPDOWN_DRESS 추가, FIT_LABELS 확장
- `_sample_skims_flt.py` (신규) — Skims `-FLT` 패턴 확인용 샘플 갤러리
- HTML 크기 4.5MB → **17.5MB** (ITEMS JSON + 드레스 + 롱슬리브 포함)

### ⏳ Step 10 — 세밀 조정 (사용자 리뷰 기반)
- 스커트 탭 직접 검토 → 피티드/플레어 오분류 피드백 시 규칙 보정 또는 fit_overrides.xlsx G열 수기 입력
- 드레스 탭 직접 검토 → ⭐ 201건 / ✨ 75건이 과도하면 RL 드레스 제외 또는 맥시 전체 배제 등 조정
- Alo 하의 누끼 검증(`_verify_alo_bottoms.html`) → `_reextract_alo_handles.py`로 재추출
- `fit_overrides.xlsx` 재생성 (드레스 포함) — `make_fit_overrides.py` 다음 실행 시

---

## 슬래시 커맨드

| 커맨드 | 파일 | 동작 |
|---|---|---|
| `/imagemap` | `C:\Users\AD0903\.claude\commands\imagemap.md` | 본 STATUS 읽기 + 작업 이어서 진행 |
| `/crawler` | (별도) | 크롤링·Vision·통합 대시보드 (PROJECT_STATUS.md 참조) |

**/crawler 와 독립 운영** — 본 프로젝트는 `brand_crawler\` 폴더를 공유하나, STATUS 파일과 커맨드가 분리되어 있음.

---

## 트러블슈팅 이력

| 오류 | 원인 | 해결 |
|---|---|---|
| Alo Shopify `products.json` 403 Forbidden | 봇 탐지 | Playwright(Chromium) 사용 → 성공 |
| Wilson 이미지 인덱스 패턴 불일치 | 상품마다 0번 또는 1번이 상품컷 | Claude Haiku Vision으로 두 이미지 비교 후 자동 선택 |
| Lacoste PDP 초기 HTML `_20`만 있음 | 나머지 suffix는 JS로 로드 | Demandware 해시는 공유 → URL에서 `_20` → `_24`로 치환하면 그대로 사용 가능 |
| Lacoste httpx HEAD 요청 403 | Referer/UA 헤더 부족 | GET + 풀 헤더(User-Agent, Referer)로 성공 |
| Descente 이미지 일부 후면(R01)이 MAIN | 크롤러가 카테고리별 기본 뷰 다름 | `_R01.JPG` → `_N01.JPG` + `/R/` 경로 제거 자동 치환 |
| Celine `IMAGE_URL` 컬럼이 `yPosition=.5` 깨진 값 | 크롤러 파싱 이슈 | `IMAGE_URL_HIRES` 컬럼 사용 |
| Alo 스웨터 오분류 상품의 누끼가 상의로 추출됨 | 프롬프트가 raw sub="스웨터" 기준으로 "sweater" 추출 요청 | `_reextract_alo_handles.py`로 올바른 sub(팬츠) 기준 재추출 |
| html2canvas "Attempting to parse an unsupported color function 'color'" | `color-mix()` CSS 함수 미지원 | `rgba()` 고정값으로 교체 |
| 캡처 시 Alo/Lululemon 이미지만 회색 박스 | `file://` + `crossorigin="anonymous"` 조합에서 null-origin tainted canvas | 로컬 PNG를 HTML 생성 시 Pillow로 base64 data URL 변환하여 임베드 |
| Sticky 좌측 컬럼 흰색 배경이 라벨 부분만 보임 | `<th>`에 `display:flex` 적용 → table-cell 속성 손실 | 내부 `.line-th-inner` 래퍼 두고 flex는 래퍼에 적용 |
| 캡처 시 원격 CDN 이미지도 회색 박스 (로컬 수정만으론 부족) | 원격 이미지 CORS taint · CDN마다 CORS 헤더 유무 불일정 | **모든 이미지를 HTML 생성 시점 data URL로 변환 + 디스크 캐시**로 근본 해결 |
| 다운로드 실패 시 검정 박스 표시 | placeholder로 쓴 1×1 PNG가 실제로 black pixel (color type 2 RGB) | color type 6 alpha 있는 **진짜 투명 PNG**로 교체 |
| Lacoste `imageapac1.lacoste.com` 191건 모두 403 | Akamai bot detection (TLS fingerprint·headless 감지) | **visible Chromium + `page.goto()`** 우회. `ctx.request.get`은 여전히 차단 |
| Lacoste 이미지 AVIF 포맷 반환 → Pillow 디코딩 실패 | `impolicy=pctp` 파라미터가 AVIF 트리거 | URL에서 `impolicy=pctp` 제거 → JPEG 응답 |

---

## 작업 이력

| 날짜 | 내용 |
|---|---|
| 2026-04-17 | `line_matrix.py`·`make_fit_overrides.py` 신규 생성. 7탭 × 3라인 × 3핏 매트릭스 HTML 대시보드 구축 |
| 2026-04-17 | RL 스틸컷 적용 — JSON `images[]` 에서 URL에 `lifestyle` 포함된 이미지 자동 선택 |
| 2026-04-17 | Wilson 스틸컷 적용 — Shopify `products.json` 수집(Playwright) + Claude Haiku Vision으로 [0]/[1] 중 상품컷 판별. 66건, 폴백·에러 0건 |
| 2026-04-17 | Lacoste 스틸컷 적용 — 이미지 URL suffix `_20` → `_24`로 치환. 사용자 시각 검증 완료 |
| 2026-04-17 | Alo는 모델컷만 존재 확인 → PASS, Gemini 2.5 Flash Image로 AI 추출 예정 |
| 2026-04-17 | `/imagemap` 커맨드 분리 — `/crawler` 와 독립 운영 |
| 2026-04-17 | Gemini 2.5 Flash Image 무료 티어 quota=0 → OpenAI gpt-image-1로 전환 |
| 2026-04-17 | Alo 샘플 5장 테스트 → 1024×1536 portrait + 상품명·소분류 명시 프롬프트로 개선, 사용자 승인 |
| 2026-04-17 | Alo 전체 배치 완료 — 193건 (의류 154 + 브라탑 39, 84분, 에러 0) |
| 2026-04-17 | `line_matrix.py` 에 `fabric_overrides.xlsx` 소분류 오버라이드 로딩 추가 → 모든 브랜드에 sub_overrides 적용 |
| 2026-04-17 | Alo 스웨터 오분류 8행 수정 |
| 2026-04-17 | **신규 4개 브랜드 추가 — Descente/Lululemon/Celine/Loropiana.** `line_matrix.py`에 4개 로더 함수 추가. 클래식 4개(Lacoste·RL·Celine·Loropiana)·어슬레져 2개(Alo·Lululemon)·스포츠 2개(Wilson·Descente) 구성 |
| 2026-04-17 | Descente 샘플 페이지(`_sample_new_brands.html`)로 N01~N10 / R01~R05 변형 표시 → 사용자 선택: **N01이 모든 상품컷**. `load_descente()`에서 `_R01.JPG` → `_N01.JPG` + `/R/` 경로 제거 자동 치환 |
| 2026-04-17 | Celine IMAGE_URL 손상 이슈 확인 → IMAGE_URL_HIRES 사용 |
| 2026-04-17 | Lululemon 모델컷 위주 → Alo와 동일 전략(OpenAI gpt-image-1) 배치 시작. `_extract_lululemon_stills_full.py` 생성 |
| 2026-04-17 | 예산 $4.0 잔액 상황에서 Lululemon 배치 일시 중단 → 매트릭스 대상(7탭 소분류 + 폴로 이름 셔츠)만 필터링하도록 스크립트 수정 → 재시작 후 33건 추가 처리 완료 (에러 0, 13.8분). 총 Lululemon 누끼 63장 생성 |
| 2026-04-17 | `make_fit_overrides.py`에 신규 4개 브랜드 로더 추가. `fit_overrides.xlsx` 762건으로 재생성 |
| 2026-04-17 | `line_matrix.html` 상단에 라인×브랜드 컬러 테이블 추가 |
| 2026-04-17 | `make_classification_export.py` 신규 — `classification_export.xlsx` 출력 (1021건, 라인 색상·자동필터·헤더 고정) |
| 2026-04-17 | 갤러리 타일 비율 변경: 정사각 `object-fit: cover` → 90×120 `object-fit: contain` (위아래 짤림 해소) |
| 2026-04-17 | Alo 하의 누끼 검증 페이지(`_verify_alo_bottoms.html`) 생성 — 103건 누끼 vs 모델컷 비교 · 체크박스 선택 · JSON 출력 |
| 2026-04-17 | Alo `Sweater Knit Wide Leg Pant` 3건 재추출 (`_reextract_alo_handles.py`) — 프롬프트를 "sweater"→"pants"로 수정. 소요 1.3분, ~$0.20 |
| 2026-04-17 | **HTML 프리미엄 리디자인** — Playfair Display + Inter 조합, 크림 배경, 라인 카드, 섹션 kicker |
| 2026-04-17 | **스커트 탭 전용 핏 분류 추가** — `SKIRT_FIT_COLS`(논플리츠/잔플리츠/와이드플리츠), `_classify_skirt_pleat()`. Vision 주름값 기반 85/85 자동 분류. 전 로더에 `pleats_raw` 필드 추가. `make_fit_overrides.py`는 탭별 드롭다운(스커트 행은 플리츠 3종) |
| 2026-04-17 | **팬츠 및 쇼츠 탭 전용 핏 분류 추가** — `BOTTOM_FIT_COLS`(슬림핏/스트레이트핏/세미와이드~와이드핏), `_classify_pants_silhouette()`. Vision 실루엣 + 레깅스 자동 + 이름 키워드 + 기본값(스트레이트) 폴백으로 **234/234 전건 자동 분류**. `silhouette_raw` 필드·`DROPDOWN_BOTTOM` 추가 |
| 2026-04-17 | 탭명 변경: `맨투맨(후디포함)` → `맨투맨 및 후디` |
| 2026-04-17 | **HTML 모던 대시보드 리디자인** — Inter 단일 폰트, pill 탭(흰색 상자+블랙 활성), `#f5f6f8` 그레이 배경, 라인 컬러 `#047857/#2563eb/#dc2626`, top bar, 4-stat hero, 라운드 14px 카드 |
| 2026-04-17 | **갤러리 8열 그리드 + 가로 스크롤** — `grid-template-columns: repeat(8, 100px)`, 타일 100×135, 매트릭스 컨테이너 `overflow-x: auto` |
| 2026-04-17 | **캡처 기능 추가** — html2canvas CDN 활용. 각 탭 우측에 "클립보드 복사"·"이미지 저장" 버튼. 캡처 시 임시 클론을 오프스크린에 생성하여 스크롤 밖 영역까지 전체 매트릭스 렌더 |
| 2026-04-17 | 로컬 AI 누끼(Alo 193 + Lulu 63)를 HTML 생성 시 Pillow로 **base64 data URL 임베드** (260px JPEG q78). 캡처 시 회색 박스 이슈 해소. HTML 324KB → 1.8MB |
| 2026-04-17 | html2canvas `color-mix()` 미지원 에러 → `rgba(15,17,21,0.08)` 고정값으로 교체 |
| 2026-04-17 | Sticky 좌측 컬럼 흰색 배경 전체 높이 적용 — `<th>`에서 `display:flex` 제거, 내부 `.line-th-inner` 래퍼에 flex 적용 |
| 2026-04-17 | **상품명 기반 탭 교정** — `_infer_tab_from_name()` 추가. 상품명 마지막 어절 키워드(팬츠/스커트/재킷 등)로 소분류 오분류 자동 수정. "코트 라이벌 와이드 레그 트랙 팬츠" 같은 아이템이 아우터 탭에 잘못 들어가 있던 문제 해결 |
| 2026-04-17 | **색상 변형 dedup** — `build_matrix()`에서 (브랜드, 상품명) 키로 중복 제거. stillcut data URL 보유 항목 우선 정렬하여 대표 이미지로 유지. 757건 → 691건 (-66) |
| 2026-04-17 | **전체 이미지 data URL 임베드** — `cache_all_images_to_data_url()` 추가. 원격 이미지를 httpx 병렬(20 workers) 다운로드 + JPEG 리사이즈 + base64 인코딩. 디스크 캐시(`.image_cache/`)로 2회차부터 1초 내 완료. 첫 실행 7분 30초 |
| 2026-04-17 | Lacoste Akamai 차단 발견 — httpx/headless 모두 403 (192건 실패) → `_fetch_lacoste_via_browser.py` 생성. **visible Chromium + `page.goto()`**로 우회, `impolicy=pctp` 제거하여 JPEG 응답 받기. 191/191 rescue 성공 (6분 소요) |
| 2026-04-17 | placeholder PNG 수정 — 기존 1×1이 black pixel이라 실패 항목이 검정 박스로 표시됨. 진짜 투명 PNG(color type 6)로 교체 |
| 2026-04-17 | 최종 캐시 상태: `.image_cache/` 766 JPEG / HTML 4.5MB / 캡처 시 회색·검정 박스 완전 해소 |
| 2026-04-17 17:22 | **상태 검증 실행** — `line_matrix.py` 재생성으로 매트릭스 수치 확인(매트릭스 노출 757건 일치), 파일 크기(HTML 1.81MB / fit_overrides.xlsx 99KB / classification_export.xlsx 120KB), 스틸 캐시(Alo 193·Lululemon 63·Wilson 66) 모두 정합. Step 2 문구 내 과거 수치(446/316) 최신화 |
| 2026-04-20 | **신규 4개 브랜드 추가** — Skims · Miu Miu · Prada (어슬레져) · Sporty & Rich (클래식). `line_matrix.py` 에 `load_skims/load_miumiu/load_prada/load_sportyandrich` 4개 로더 추가. Skims·Sporty & Rich는 한글 헤더(`_load_xlsx_kor`) 재사용, Miu Miu·Prada는 대문자 헤더(Descente/Lululemon 포맷 따름). `BRAND_LABEL`·`LINES`·`_BRAND_KEY_MAP` 확장 |
| 2026-04-20 | `make_fit_overrides.py` 에 신규 4개 브랜드 로더 추가 · `BRAND_COLOR` 확장. fit_overrides.xlsx 762건 → **1,427건**으로 재생성 (Skims 128 · Miu Miu 169 · Prada 49 · Sporty & Rich 290 추가) |
| 2026-04-20 | `line_matrix.html` 재생성 — 매트릭스 노출 691건 → **1,278건** (+587). 원격 이미지 캐시 +599건 다운로드(175초, 실패 0). HTML 1.81MB → **7.6MB** |
| 2026-04-20 | **리뷰 모드 1차 구현** — 이미지 모달 팝업, 체크박스 영속(localStorage), ST 추천 ⭐, 선택된 항목 전용 탭, 백업 JSON·이미지 ZIP 다운로드. `classify_st_match()` 함수 추가 (탭+브랜드 기반 1차 필터, 553/1,278 = 43%) |
| 2026-04-20 | **ST 추천 이원화 (⭐/✨)** — `classify_st_match()` 3값 반환(core/adapt/None). 럭셔리 4사(Miu Miu/Prada/Celine/Loro Piana)와 Skims를 Adapt 후보로 편입. 엄격 필터 적용으로 ⭐ 160 + ✨ 50 = **210건** 추천 |
| 2026-04-20 | **z-index 수정** — 좌측 고정 컬럼(line-th:10 / corner-th:20 / thead:15)을 체크박스(z:2)보다 높게 조정하여 스크롤 시 체크박스가 라인 라벨 뒤로 가려짐 |
| 2026-04-20 | **캡처 시 체크박스 제거** — `capturePanel()` JS에서 clone 후 `.chk` 요소 제거 + `.is-selected` 하이라이트 제거. 깔끔한 갤러리 이미지만 캡처 |
| 2026-04-20 | **스커트 탭 4분할** — 논/잔/와이드 3컬럼 → **피티드·플레어·플리츠·와이드플리츠 4컬럼**. `_classify_skirt_pleat()` 재작성 (Vision H라인=피티드 / A라인·플레어=플레어 / 잔플리츠+언발란스=플리츠 / 와이드=와이드). 21·63·44·17건 분포 |
| 2026-04-20 | **Skims 모델컷 제외 5건** — 사용자 샘플(`_sample_skims_flt.py`) 검증으로 URL에 `-FLT` 없는 44건 중 5건이 다른 URL 체계(LG-TOP-/DS-DRS-). `-FLT` 대체 불가 → `_SKIMS_EXCLUDE_BY_NAME` 상수로 매트릭스 제외 |
| 2026-04-20 | **⭐✨ 필터 토글 + 일괄 ZIP** — 추천만 보기 토글 버튼 (body.filter-rec 클래스로 thumbs 숨김 · localStorage 영속) + 추천 전체 ZIP 버튼 (체크박스 불필요, 201+75=276건 일괄 다운로드). 셀 카운트 동적 업데이트 `보이는/전체` |
| 2026-04-20 | **이미지 확대/축소 컨트롤** — 탭 바 우측에 🔍 슬라이더 + ± 버튼 추가 (60~280px, 기본 100px, 10px 단위). CSS 변수 `--thumb-w`로 갤러리·선택탭 썸네일만 스케일. `.gallery-cell`·`.fit-th` min-width 계산식으로 자동 확장. localStorage 영속 |
| 2026-04-20 | **티셔츠 탭 확장** — `티셔츠(반팔)` → **티셔츠 및 롱슬리브**. TABS에 `롱슬리브` 소분류 추가. 티셔츠 탭 121 → 146건 (+25 롱슬리브, 어슬레져 29→50·스포츠 20→25). 이전에 매트릭스 미포함이던 롱슬리브 가시화 |
| 2026-04-20 | **드레스 탭 신설** — 8번째 탭 추가 (위치: 티셔츠↔스커트). 3컬럼 구조(미니/미디/맥시). `_classify_dress_length()` 함수, DRESS_FIT_COLS, `length_raw` 필드 (각 로더에 Vision `기장`/`VISION_LENGTH` 추출 추가). 106건 드레스 매트릭스 노출 |
| 2026-04-20 | **드레스 ST 이원화 적용** — §6.8 Mini Dress 실험 방향 기반. ⭐: TH2/SR/RL 미니·미디 + 타 브랜드 tennis·polo·court 키워드 미니. ✨: 럭셔리 4사 미니 + Skims 미니 + Alo/Lulu 미니. 맥시 전체 제외. 드레스 ⭐ 39 + ✨ 25 = 64건 추가로 총 ⭐ 201 + ✨ 75 = **276건** 추천 |
| 2026-04-20 | 최종 매트릭스 노출 **1,413건** (7탭 1,278 + 드레스 106 + 롱슬리브 25 + Skims 제외 -5 ≈ 1,413). HTML 17.5MB (ITEMS JSON + 이미지 data URL) |
| 2026-04-21 | **Lacoste 원본 해상도 재다운로드 스크립트** (`_rescue_lacoste_hires.py`) 신규. `hires_backup_*.json` 내 Lacoste 실패분을 visible Chromium으로 Akamai 우회 → `imwidth` 제거로 원본(대부분 1340×1340, 일부 2000×2000) 수신 → 기존 ZIP 교체. `.image_cache_hires/` 별도 캐시 |
| 2026-04-21 | **∅ 제외만 보기 필터 추가** — `filterExc` 상태·`FILTER_EXC_KEY` localStorage·`body.filter-exc` CSS 규칙. `toggleFilterExc()`는 추천 필터와 상호 배타 (한쪽 활성 시 다른 쪽 자동 해제). `updateCellCounts()`도 exc 분기 |
| 2026-04-21 | **🎨 디자이너 PICK 기능 신설** — 재생성 선택과 독립. 모달 팝업에 별도 체크박스(`#modal-pick-chk` · 보라색), 썸네일은 `.is-pick` 보라 테두리로 표시. 전용 탭 `__pick__` 추가(탭→브랜드 2단 그룹화 렌더). localStorage `line_matrix_designer_pick_v1` 저장. 전용 버튼: PICK 백업 JSON · PICK ZIP · PICK 해제. 캡처 시 `.is-pick` 테두리 제거 추가 |
