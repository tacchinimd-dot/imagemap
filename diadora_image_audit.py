"""
Diadora 상품컷 vs 모델컷 분석 샘플 HTML 생성기.

추천(CORE/ADAPT) 대상 Diadora 상품의 모든 상세 이미지를
side-by-side로 비교할 수 있는 단일 HTML 생성.

과정:
1. 추천 목록(classify_st_match == core|adapt) Diadora 의류 추출
2. 각 상품의 product_url → JSON-LD image 배열 fetch (concurrent)
3. 각 이미지를 base64 data URL로 임베드 (CORS 회피)
4. 카드 그리드 HTML: 상품별로 index 0~N을 가로로 나열

출력: diadora_image_audit.html
"""
from __future__ import annotations
import base64
import concurrent.futures as cf
import html
import io
import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import httpx
from PIL import Image

from line_matrix import (
    classify_st_match,
    classify_tab,
    load_diadora,
)

BASE = Path(__file__).parent
CACHE_DIR = BASE / ".diadora_audit_cache"
CACHE_DIR.mkdir(exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA}


def fetch_product_images(product_url: str) -> list[str]:
    """상품 상세 페이지 JSON-LD에서 image 배열 추출."""
    try:
        r = httpx.get(product_url, headers=HEADERS, timeout=25, follow_redirects=True)
        if r.status_code != 200:
            return []
        blocks = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            r.text, re.S)
        for b in blocks:
            try:
                d = json.loads(b.strip())
            except Exception:
                continue
            if isinstance(d, dict) and d.get("@type") == "Product":
                imgs = d.get("image", [])
                if isinstance(imgs, str):
                    imgs = [imgs]
                elif isinstance(imgs, dict):
                    imgs = [imgs.get("contentUrl") or imgs.get("url")]
                out = []
                for x in imgs:
                    if isinstance(x, dict):
                        x = x.get("contentUrl") or x.get("url")
                    if isinstance(x, str):
                        x = x.replace("https:https://", "https://")
                        out.append(x)
                return out
    except Exception as e:
        print(f"  [fetch 실패] {product_url}: {e}")
    return []


def img_to_data_url(url: str, max_w: int = 320, q: int = 80) -> str | None:
    """이미지 URL → base64 JPEG data URL. 디스크 캐시 사용."""
    import hashlib
    h = hashlib.md5(url.encode()).hexdigest()
    cpath = CACHE_DIR / f"{h}.jpg"
    if not cpath.exists():
        try:
            r = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
            if r.status_code != 200:
                return None
            img = Image.open(io.BytesIO(r.content))
            if img.mode not in ("RGB",):
                img = img.convert("RGB")
            if img.width > max_w:
                ratio = max_w / img.width
                img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
            img.save(cpath, "JPEG", quality=q, optimize=True)
        except Exception as e:
            print(f"    [img 실패] {url}: {e}")
            return None
    try:
        b64 = base64.b64encode(cpath.read_bytes()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return None


def render_html(rows: list[dict], prefilled: dict[str, int]) -> str:
    cards_html = []
    for r in rows:
        name = r["name"]
        init_idx = prefilled.get(name)  # 사용자가 이미 지정한 index (없으면 None)
        imgs_html = []
        for i, img in enumerate(r["images"]):
            data_url = img["data_url"]
            kind = "main (크롤러 대표)" if i == 0 else f"extra [{i}]"
            if not data_url:
                imgs_html.append(
                    f'<div class="img-slot broken" data-idx="{i}">'
                    f'<div class="ph">loading failed</div>'
                    f'<div class="meta">[{i}] {kind}</div></div>')
                continue
            is_selected = (init_idx == i)
            sel_cls = " selected" if is_selected else ""
            imgs_html.append(
                f'<div class="img-slot{sel_cls}" data-idx="{i}" onclick="selectIdx(this)">'
                f'<img src="{data_url}" alt="{i}" loading="lazy">'
                f'<div class="meta">[{i}] {kind}</div>'
                f'<div class="check">✓</div>'
                f'</div>')
        mark_badge = f'<span class="badge {r["st_match"]}">{"⭐ CORE" if r["st_match"]=="core" else "✨ ADAPT"}</span>'
        done_cls = " card-done" if init_idx is not None else ""
        cards_html.append(f"""
        <div class="card{done_cls}" data-name="{html.escape(name)}" data-tab="{html.escape(r['tab'] or '')}" data-mark="{r['st_match']}" data-initial="{init_idx if init_idx is not None else ''}">
          <div class="card-head">
            <div class="name"><a href="{html.escape(r['product_url'])}" target="_blank">{html.escape(name)}</a></div>
            <div class="info">{mark_badge} <span class="tag">{html.escape(r['tab_label'] or '')}</span> <span class="tag">{html.escape(r['sub'] or '')}</span> <span class="pick-status"></span></div>
          </div>
          <div class="img-row">{''.join(imgs_html)}</div>
        </div>""")

    prefilled_json = json.dumps(prefilled, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8">
<title>Diadora 이미지 패턴 분석 (모델컷 vs 상품컷)</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#222;padding:24px}}
.header{{background:#E4002B;color:#fff;padding:20px 24px;border-radius:10px;margin-bottom:20px}}
.header h1{{font-size:20px;font-weight:700;letter-spacing:1px}}
.header p{{font-size:13px;opacity:.9;margin-top:6px;line-height:1.6}}
.legend{{background:#fff;padding:14px 20px;border-radius:8px;margin-bottom:20px;font-size:12px;line-height:1.9;box-shadow:0 2px 6px rgba(0,0,0,.05)}}
.legend b{{color:#E4002B}}
.toolbar{{position:sticky;top:0;background:#fff;padding:12px 20px;border-radius:8px;margin-bottom:18px;box-shadow:0 2px 6px rgba(0,0,0,.05);display:flex;gap:10px;flex-wrap:wrap;z-index:100;align-items:center}}
.tab-btn{{padding:6px 14px;background:#f0f0f0;border:none;border-radius:6px;font-size:12px;cursor:pointer;transition:.15s}}
.tab-btn.active{{background:#E4002B;color:#fff;font-weight:700}}
.tab-btn:hover:not(.active){{background:#e0e0e0}}
.action-btn{{padding:7px 16px;background:#16a34a;color:#fff;border:none;border-radius:6px;font-size:12px;cursor:pointer;font-weight:700;letter-spacing:.3px;transition:.15s}}
.action-btn:hover{{background:#15803d}}
.action-btn.secondary{{background:#6b7280}}
.action-btn.secondary:hover{{background:#4b5563}}
.count-label{{font-size:12px;color:#888}}
.progress-label{{font-size:12px;color:#16a34a;font-weight:700;margin-left:auto}}
.grid{{display:grid;grid-template-columns:1fr;gap:14px;max-width:1600px;margin:0 auto}}
.card{{background:#fff;border-radius:10px;padding:14px;box-shadow:0 2px 6px rgba(0,0,0,.07);transition:border .15s}}
.card.hidden{{display:none}}
.card.card-done{{border-left:4px solid #16a34a}}
.card-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid #eee;flex-wrap:wrap;gap:8px}}
.name{{font-size:14px;font-weight:600}}
.name a{{color:#222;text-decoration:none}}
.name a:hover{{color:#E4002B;text-decoration:underline}}
.info{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.badge{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:10px}}
.badge.core{{background:#fef3c7;color:#92400e}}
.badge.adapt{{background:#dbeafe;color:#1e40af}}
.tag{{font-size:11px;color:#666;background:#f0f0f0;padding:3px 8px;border-radius:10px}}
.pick-status{{font-size:11px;color:#16a34a;font-weight:700}}
.img-row{{display:flex;gap:10px;overflow-x:auto;padding:4px 2px;scroll-snap-type:x mandatory}}
.img-slot{{flex:0 0 180px;scroll-snap-align:start;position:relative;border:2px solid transparent;border-radius:8px;overflow:hidden;background:#fafafa;cursor:pointer;transition:.15s}}
.img-slot:hover{{border-color:#cbd5e1;transform:translateY(-2px)}}
.img-slot.selected{{border-color:#16a34a;box-shadow:0 0 0 3px rgba(22,163,74,.25)}}
.img-slot.broken{{border-color:#ddd;background:#f0f0f0;cursor:not-allowed}}
.img-slot img{{width:100%;height:240px;object-fit:contain;display:block;background:#fff;pointer-events:none}}
.img-slot .meta{{padding:6px 8px;background:rgba(0,0,0,.72);color:#fff;font-size:10px;position:absolute;bottom:0;left:0;right:0;letter-spacing:.3px;pointer-events:none}}
.img-slot.selected .meta{{background:#16a34a}}
.img-slot .ph{{height:240px;display:flex;align-items:center;justify-content:center;color:#999;font-size:11px}}
.img-slot .check{{position:absolute;top:8px;right:8px;width:26px;height:26px;background:#16a34a;color:#fff;border-radius:50%;display:none;align-items:center;justify-content:center;font-weight:700;font-size:14px;box-shadow:0 2px 6px rgba(0,0,0,.2);pointer-events:none}}
.img-slot.selected .check{{display:flex}}
</style>
</head><body>
<div class="header">
<h1>🔍 Diadora 이미지 패턴 분석 — 모델컷 vs 상품컷 검토</h1>
<p>각 상품의 상세 페이지 JSON-LD image 배열을 모두 표시. <b>상품컷인 이미지를 클릭</b>하면 선택되어 좌측 녹색 바로 표시됩니다.<br>
선택은 브라우저에 자동 저장(localStorage)되며, 상단 <b>📥 선택 결과 JSON 다운로드</b> 버튼으로 언제든 내보낼 수 있습니다.</p>
</div>
<div class="legend">
<b>URL 경로 차이</b>:
<code>[0]</code> = <code>/web/product/big/YYYYMM/</code> (메인 — 크롤러 기본값)
&nbsp;·&nbsp;
<code>[1~]</code> = <code>/web/product/extra/big/YYYYMMDD/</code> (추가)<br>
<b>🟢 이미 사용자가 지정한 {sum(1 for v in prefilled.values() if v is not None)}개 상품은 초록 체크 ✓</b>로 표시되어 있습니다. 나머지도 동일한 방식으로 클릭해주세요.
</div>
<div class="toolbar">
  <button class="tab-btn active" data-filter="all">전체 ({len(rows)})</button>
  <button class="tab-btn" data-filter="core">⭐ CORE</button>
  <button class="tab-btn" data-filter="adapt">✨ ADAPT</button>
  <button class="tab-btn" data-filter="outer">아우터</button>
  <button class="tab-btn" data-filter="skirt">스커트</button>
  <button class="tab-btn" data-filter="dress">드레스</button>
  <button class="tab-btn" data-filter="bottom">팬츠·쇼츠</button>
  <button class="tab-btn" data-filter="sweat">맨투맨·후디</button>
  <button class="tab-btn" data-filter="tee">티셔츠·롱슬리브</button>
  <button class="tab-btn" data-filter="todo">미선택만</button>
  <button class="action-btn" onclick="exportJSON()">📥 선택 결과 JSON 다운로드</button>
  <button class="action-btn secondary" onclick="if(confirm('로컬 저장을 모두 초기화할까요? (초기 20개 사전 지정은 유지)')) resetAll()">🔄 초기화</button>
  <span class="count-label" id="visible-count">{len(rows)}개 표시</span>
  <span class="progress-label" id="progress">선택 진행 로드 중…</span>
</div>
<div class="grid">{''.join(cards_html)}</div>
<script>
const STORAGE_KEY = 'diadora_still_picks_v1';
const PREFILLED = {prefilled_json};
let state = (() => {{
  try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') || {{}}; }}
  catch {{ return {{}}; }}
}})();
// prefilled 병합 (브라우저 비어 있으면 초기 지정분을 주입)
Object.keys(PREFILLED).forEach(k => {{ if (!(k in state) && PREFILLED[k] !== null) state[k] = PREFILLED[k]; }});
save();

function save() {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); updateProgress(); }}

function selectIdx(slot) {{
  const card = slot.closest('.card');
  const name = card.dataset.name;
  const idx = parseInt(slot.dataset.idx, 10);
  // 토글: 이미 선택된 걸 또 누르면 해제
  const current = state[name];
  if (current === idx) {{
    delete state[name];
    card.classList.remove('card-done');
    card.querySelectorAll('.img-slot.selected').forEach(s => s.classList.remove('selected'));
    card.querySelector('.pick-status').textContent = '';
  }} else {{
    state[name] = idx;
    card.classList.add('card-done');
    card.querySelectorAll('.img-slot').forEach(s => s.classList.toggle('selected', parseInt(s.dataset.idx,10) === idx));
    card.querySelector('.pick-status').textContent = `✓ [${{idx}}] 선택`;
  }}
  save();
}}

function updateProgress() {{
  const total = document.querySelectorAll('.card').length;
  const done = Object.keys(state).length;
  document.getElementById('progress').textContent = `✓ ${{done}} / ${{total}} 선택`;
  // 카드별 상태 표시 갱신
  document.querySelectorAll('.card').forEach(c => {{
    const name = c.dataset.name;
    const v = state[name];
    c.classList.toggle('card-done', v !== undefined);
    c.querySelectorAll('.img-slot').forEach(s => {{
      s.classList.toggle('selected', v !== undefined && parseInt(s.dataset.idx,10) === v);
    }});
    const ps = c.querySelector('.pick-status');
    if (ps) ps.textContent = v !== undefined ? `✓ [${{v}}] 선택` : '';
  }});
}}

function exportJSON() {{
  // {{상품명: index}} 형태 + 메타데이터
  const out = {{
    generated_at: new Date().toISOString(),
    total: Object.keys(state).length,
    overrides: state
  }};
  const blob = new Blob([JSON.stringify(out, null, 2)], {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'diadora_still_picks_' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
}}

function resetAll() {{
  state = {{}};
  Object.keys(PREFILLED).forEach(k => {{ if (PREFILLED[k] !== null) state[k] = PREFILLED[k]; }});
  save();
}}

// 필터
document.querySelectorAll('.tab-btn').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.tab-btn').forEach(x => x.classList.remove('active'));
  b.classList.add('active');
  const f = b.dataset.filter;
  let shown = 0;
  document.querySelectorAll('.card').forEach(c => {{
    const tab = c.dataset.tab;
    const mark = c.dataset.mark;
    const isDone = state[c.dataset.name] !== undefined;
    let ok;
    if (f === 'all') ok = true;
    else if (f === 'todo') ok = !isDone;
    else ok = (f === mark || f === tab);
    c.classList.toggle('hidden', !ok);
    if (ok) shown++;
  }});
  document.getElementById('visible-count').textContent = shown + '개 표시';
}}));

updateProgress();
</script>
</body></html>"""


TAB_LABEL = {
    "outer":"아우터","polo":"폴로","tee":"티셔츠·롱슬리브","dress":"드레스",
    "skirt":"스커트","sweat":"맨투맨·후디","sweater":"스웨터","bottom":"팬츠·쇼츠",
}


def main():
    items = load_diadora()
    # CORE/ADAPT만
    targets = []
    for it in items:
        tab = classify_tab(it)
        if not tab:
            continue
        st = classify_st_match(it, tab)
        if st not in ("core", "adapt"):
            continue
        targets.append({
            **it,
            "tab": tab,
            "tab_label": TAB_LABEL.get(tab, tab),
            "sub": it.get("sub_raw", ""),
            "st_match": st,
        })
    # 정렬: mark → tab → name
    order = {"core": 0, "adapt": 1}
    targets.sort(key=lambda x: (order[x["st_match"]], x["tab"], x["name"]))
    print(f"대상 {len(targets)}건 (CORE+ADAPT)")

    # product detail fetch
    print("[1/2] JSON-LD image 배열 수집 중...")
    def _fetch_one(it):
        urls = fetch_product_images(it["product_url"])
        return it, urls
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(_fetch_one, targets))
    print(f"  → {time.time()-t0:.1f}s 소요")

    # image fetch + data url
    print("[2/2] 이미지 다운로드 및 data URL 변환 중...")
    all_img_urls = []
    for it, urls in results:
        all_img_urls.extend(urls)
    seen = set()
    uniq = [u for u in all_img_urls if u and not (u in seen or seen.add(u))]
    print(f"  고유 이미지 {len(uniq)}개")
    t0 = time.time()
    url2data = {}
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for url, data in zip(uniq, ex.map(img_to_data_url, uniq)):
            url2data[url] = data
    ok = sum(1 for v in url2data.values() if v)
    print(f"  → {time.time()-t0:.1f}s, 성공 {ok}/{len(uniq)}")

    # 데이터 구성
    rows = []
    for it, urls in results:
        imgs = [{"url": u, "data_url": url2data.get(u)} for u in urls[:8]]
        rows.append({
            "name": it["name"],
            "product_url": it["product_url"],
            "tab": it["tab"],
            "tab_label": it["tab_label"],
            "sub": it["sub"],
            "st_match": it["st_match"],
            "images": imgs,
        })
    # 오버라이드 JSON 로드 (사용자가 미리 지정한 20개)
    ov_path = BASE / "diadora_still_overrides.json"
    prefilled: dict[str, int] = {}
    if ov_path.exists():
        try:
            d = json.loads(ov_path.read_text(encoding="utf-8"))
            prefilled = d.get("overrides", {}) or {}
            print(f"오버라이드 {len(prefilled)}건 로드")
        except Exception as e:
            print(f"오버라이드 로드 실패: {e}")

    out = BASE / "diadora_image_audit.html"
    out.write_text(render_html(rows, prefilled), encoding="utf-8")
    print(f"\n[완료] {out}  ({out.stat().st_size/1024:.1f}KB)")


if __name__ == "__main__":
    main()
