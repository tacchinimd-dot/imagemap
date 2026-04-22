-- ============================================================
-- F&F Brand Matrix · Supabase 스키마
-- ============================================================
-- 실행 방법:
--   1) https://supabase.com 프로젝트 생성 (무료 티어 OK)
--   2) 좌측 "SQL Editor" 메뉴 > 새 쿼리 > 이 파일 전체 붙여넣기 > Run
--   3) 좌측 "Authentication" > "Providers" > Email 활성화 (기본 ON)
--   4) 좌측 "Authentication" > "URL Configuration"
--        Site URL: https://tacchinimd-dot.github.io/imagemap/
--        Redirect URLs: https://tacchinimd-dot.github.io/imagemap/**
--                       http://localhost:** (로컬 테스트용 · 선택)
--   5) "Settings" > "API" 에서 Project URL, anon public key 복사
--        → 터미널에서 환경변수 등록 또는 line_matrix.py 상단 상수에 입력
--
-- 보안 모델:
--   - anon key는 HTML에 노출되어도 안전 (설계상 public)
--   - RLS 정책이 실제 보안을 담당 — 팀 도메인(@fnfcorp.com) 외 접근 차단
-- ============================================================


-- ── 1. 테이블 ─────────────────────────────────────────────────
-- MD PICK (이미지 재생성 후보 선정 · 개인별)
create table if not exists md_picks (
    user_email   text        not null,
    item_id      text        not null,
    created_at   timestamptz not null default now(),
    primary key (user_email, item_id)
);

-- 디자이너 PICK (독립 · 개인별)
create table if not exists designer_picks (
    user_email   text        not null,
    item_id      text        not null,
    created_at   timestamptz not null default now(),
    primary key (user_email, item_id)
);

-- 조회 성능용 인덱스 (item_id 로 역조회 · 누가 선택했는지)
create index if not exists idx_md_picks_item       on md_picks(item_id);
create index if not exists idx_designer_picks_item on designer_picks(item_id);


-- ── 2. Realtime 활성화 ────────────────────────────────────────
-- supabase_realtime 은 기본 publication. 이 테이블을 포함시켜야 postgres_changes 이벤트가 전파됨.
alter publication supabase_realtime add table md_picks;
alter publication supabase_realtime add table designer_picks;


-- ── 3. RLS (Row-Level Security) ──────────────────────────────
alter table md_picks       enable row level security;
alter table designer_picks enable row level security;

-- 읽기: @fnfcorp.com 이메일로 로그인한 사용자 전체 (팀원 모두 상대 PICK 조회 가능)
drop policy if exists "team_read_md" on md_picks;
create policy "team_read_md" on md_picks for select
    using (auth.jwt()->>'email' ilike '%@fnfcorp.com');

drop policy if exists "team_read_dp" on designer_picks;
create policy "team_read_dp" on designer_picks for select
    using (auth.jwt()->>'email' ilike '%@fnfcorp.com');

-- 쓰기: 본인 이메일 row 만 insert 가능 + 도메인 체크
drop policy if exists "self_insert_md" on md_picks;
create policy "self_insert_md" on md_picks for insert
    with check (
        auth.jwt()->>'email' = user_email
        and user_email ilike '%@fnfcorp.com'
    );

drop policy if exists "self_insert_dp" on designer_picks;
create policy "self_insert_dp" on designer_picks for insert
    with check (
        auth.jwt()->>'email' = user_email
        and user_email ilike '%@fnfcorp.com'
    );

-- 삭제: 본인 것만
drop policy if exists "self_delete_md" on md_picks;
create policy "self_delete_md" on md_picks for delete
    using (auth.jwt()->>'email' = user_email);

drop policy if exists "self_delete_dp" on designer_picks;
create policy "self_delete_dp" on designer_picks for delete
    using (auth.jwt()->>'email' = user_email);


-- ── 4. 선택사항: 현재 상태 빠른 조회 뷰 ──────────────────────
-- 모든 MD PICK 항목 + 선택한 사람 수 집계
create or replace view v_md_picks_summary as
select item_id, count(*) as picker_count, array_agg(user_email order by created_at) as pickers
from md_picks group by item_id;

create or replace view v_designer_picks_summary as
select item_id, count(*) as picker_count, array_agg(user_email order by created_at) as pickers
from designer_picks group by item_id;


-- ============================================================
-- 검증 쿼리 (옵션)
-- ============================================================
-- 1) 테이블 확인:    select count(*) from md_picks;
-- 2) Realtime 확인:   select * from pg_publication_tables where pubname = 'supabase_realtime';
-- 3) 정책 확인:       select * from pg_policies where tablename in ('md_picks','designer_picks');
