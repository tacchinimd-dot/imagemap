"""Lacoste 원본 해상도 재다운로드 → 기존 hires ZIP에 교체 반영.

다운로드 방식: visible Chromium + page.goto() (Akamai 우회 · _fetch_lacoste_via_browser.py와 동일).
차이점: 260px 축소 없이 원본 해상도 JPEG 그대로 ZIP에 쓴다.

사용:
    python _rescue_lacoste_hires.py \
        --json "C:\\Users\\AD0903\\Downloads\\hires_backup_2026-04-20-09-18-35.json" \
        --zip  "C:\\Users\\AD0903\\Downloads\\hires_backup_2026-04-20-09-18-35_hires.zip"
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

HIRES_CACHE_DIR = Path(r"C:\Users\AD0903\brand_crawler") / ".image_cache_hires"


def normalize_lacoste_url(url: str) -> str:
    """impolicy=pctp 제거 + imwidth 제거 → 2000x2000 원본 JPEG 요청."""
    url = re.sub(r"[&?]impolicy=[^&]*", "", url)
    url = re.sub(r"[&?]imwidth=\d+", "", url)
    # Demandware는 ?만 남으면 무시하지만 &로 시작하면 에러 — 정리
    url = re.sub(r"\?&", "?", url)
    return url.rstrip("?&")


def safe_filename(s: str, max_len: int = 80) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", s).strip()[:max_len]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="백업 JSON 경로")
    ap.add_argument("--zip", required=True, help="기존 hires ZIP 경로 (수정됨)")
    ap.add_argument("--retry", type=int, default=2, help="실패 시 재시도 횟수")
    ap.add_argument("--force", action="store_true",
                    help="이미 OK 상태인 Lacoste 항목도 재다운로드")
    args = ap.parse_args()

    import json as _json

    json_path = Path(args.json)
    zip_path = Path(args.zip)
    data = _json.loads(json_path.read_text(encoding="utf-8"))
    items = data["items"]

    # 기존 ZIP에서 manifest.csv 읽어 재다운로드 대상 추리기
    with zipfile.ZipFile(zip_path, "r") as zf:
        manifest_text = zf.read("manifest.csv").decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(manifest_text)))
    header = rows[0]
    idx_no = header.index("순번")
    idx_brand = header.index("브랜드")
    idx_status = header.index("상태")
    idx_file = header.index("이미지파일")

    # Lacoste 중 원본 다운로드가 필요한 항목 (캐시복구 · 실패 둘 다)
    targets = []
    for r in rows[1:]:
        if r[idx_brand] != "Lacoste":
            continue
        status = r[idx_status]
        if status.startswith("OK") and not args.force:
            continue
        num = int(r[idx_no])
        it = items[num - 1]
        url = it.get("image_hires") or it.get("image_url") or ""
        if "lacoste.com" not in url:
            continue
        targets.append((num, it, url))

    print(f"대상: {len(targets)}건 (visible Chromium 사용)")
    if not targets:
        print("대상 없음 — 종료")
        return

    HIRES_CACHE_DIR.mkdir(exist_ok=True)

    t0 = time.time()
    results = {}  # num -> bytes (원본 JPEG)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1200, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        for i, (num, it, url) in enumerate(targets, 1):
            fetch_url = normalize_lacoste_url(url)
            key = hashlib.md5(url.encode()).hexdigest()
            cached = HIRES_CACHE_DIR / f"{key}.jpg"

            if cached.exists() and cached.stat().st_size > 2000:
                results[num] = cached.read_bytes()
                size_kb = cached.stat().st_size // 1024
                if i % 10 == 0:
                    print(f"  [{i}/{len(targets)}] cached {num} ({size_kb}KB)")
                continue

            body = None
            for attempt in range(args.retry + 1):
                try:
                    r = page.goto(fetch_url, timeout=20000)
                    if r and r.status == 200:
                        b = r.body()
                        if len(b) > 2000:
                            body = b
                            break
                except Exception:
                    pass
                if attempt < args.retry:
                    time.sleep(1)

            if body:
                cached.write_bytes(body)
                results[num] = body
                size_kb = len(body) // 1024
                mark = "✓"
            else:
                size_kb = 0
                mark = "✗"

            if i % 10 == 0 or i == len(targets) or mark == "✗":
                elapsed = time.time() - t0
                eta = elapsed / i * (len(targets) - i)
                print(
                    f"  [{i:>3}/{len(targets)}] {mark} [{num}] "
                    f"{it.get('name','')[:40]} ({size_kb}KB) "
                    f"— {elapsed:.1f}s elapsed, ETA {eta/60:.1f}m"
                )

        browser.close()

    print(f"\n다운로드 완료: {len(results)}/{len(targets)} ({(time.time()-t0)/60:.1f}분)")

    # ZIP 업데이트 (실패분은 기존 캐시복구본 유지)
    tmp_path = zip_path.with_suffix(".zip.tmp")
    new_manifest = [header]

    with zipfile.ZipFile(zip_path, "r") as zin, zipfile.ZipFile(
        tmp_path, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        # 기존 파일 목록 중 교체 대상 파일명 수집
        replaced_files = set()
        for r in rows[1:]:
            num = int(r[idx_no])
            if num in results:
                replaced_files.add(r[idx_file])

        # 기존 ZIP 내 파일 복사 (교체 대상 제외)
        for name in zin.namelist():
            if name == "manifest.csv" or name in replaced_files:
                continue
            zout.writestr(name, zin.read(name))

        # 신규 hires 이미지 쓰기 + manifest 업데이트
        for r in rows[1:]:
            num = int(r[idx_no])
            if num in results:
                body = results[num]
                it = items[num - 1]
                brand = it.get("brand", "")
                name_ = it.get("name", "")
                tab = it.get("tab", "")
                fname = (
                    f"{num:04d}_{safe_filename(tab, 20)}_"
                    f"{safe_filename(f'{brand}_{name_}')}.jpg"
                )
                zout.writestr(fname, body)
                size_kb = len(body) // 1024
                new_r = list(r)
                new_r[idx_file] = fname
                new_r[idx_status] = f"OK-원본 ({size_kb}KB)"
                new_manifest.append(new_r)
            else:
                new_manifest.append(r)

        buf = io.StringIO()
        csv.writer(buf).writerows(new_manifest)
        zout.writestr("manifest.csv", "\ufeff" + buf.getvalue())

    shutil.move(str(tmp_path), str(zip_path))
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"\n[완료] ZIP 업데이트: {zip_path.name} ({size_mb:.1f}MB)")
    print(f"  원본 해상도 교체: {len(results)}건")
    if len(results) < len(targets):
        print(f"  미복구: {len(targets) - len(results)}건 (기존 캐시복구본 유지)")


if __name__ == "__main__":
    main()
