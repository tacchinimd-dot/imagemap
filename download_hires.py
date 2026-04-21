"""고화질 이미지 다운로드 — line_matrix.html의 백업 JSON을 입력으로 원본 해상도 이미지 ZIP 생성.

브라우저의 fetch() CORS 제약을 우회하기 위한 Python 스크립트.
HTML의 🔥 고화질용 백업 버튼으로 추출한 JSON을 입력받아 httpx로 직접 다운로드.

사용법:
    python download_hires.py hires_backup_YYYY-MM-DD-HH-MM-SS.json
    python download_hires.py hires_backup_*.json --out custom_out.zip
    python download_hires.py hires_backup_*.json --workers 20

JSON 구조 (items 배열):
    {
      "image_hires": "file:///C:/...alo_crawler/stills/xxx.png"  또는
                     "https://cdn.shopify.com/..."  또는
                     "data:image/jpeg;base64,..."  (이 경우는 썸네일 임베드 → hires 불가)
      "image_thumb": "data:image/jpeg;base64,..."  (폴백용)
      기타 메타데이터 (brand, tab, fit, name, product_url, st_mark 등)
    }

동작:
    - file:///: 로컬 PNG/JPG 파일 복사 (원본 해상도)
    - https://: httpx.get()로 원본 다운로드 (CORS 무관)
    - data:image/...: 이미 embed된 저해상 썸네일이라 건너뜀 or 실패 처리
"""
from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import re
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    import httpx
except ImportError:
    print("❌ httpx 필요: pip install httpx", file=sys.stderr)
    sys.exit(1)

sys.stdout.reconfigure(encoding="utf-8")


_HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept": "*/*",
    },
]


def safe_filename(s: str, max_len: int = 80) -> str:
    """Windows·Linux 공통 안전 파일명 (특수문자 제거)."""
    return re.sub(r'[\\/:*?"<>|]', '_', s).strip()[:max_len]


def file_url_to_path(url: str) -> Path | None:
    """`file:///C:/...` → Path 객체."""
    parsed = urlparse(url)
    if parsed.scheme != "file":
        return None
    p = unquote(parsed.path)
    if sys.platform == "win32" and p.startswith("/"):
        p = p[1:]  # "/C:/foo" → "C:/foo"
    return Path(p)


def fetch_image(url: str, timeout: int = 30, retries: int = 2) -> tuple[bytes | None, str | None, str | None]:
    """이미지 다운로드 · (content, ext, error) 반환."""
    if not url:
        return None, None, "image_hires 비어있음"

    # data URL → 이미 embed된 저해상 썸네일, hires 다운로드 대상 아님
    if url.startswith("data:"):
        try:
            header, payload = url.split(",", 1)
            mime_match = re.match(r"data:([^;]+)", header)
            mime = mime_match.group(1) if mime_match else "image/jpeg"
            ext = mime.split("/")[-1].replace("jpeg", "jpg")
            content = base64.b64decode(payload)
            return content, ext, "(data URL 폴백 — 저해상 썸네일)"
        except Exception as e:
            return None, None, f"data URL 파싱 실패: {e}"

    # file:// → 로컬 복사
    if url.startswith("file://"):
        path = file_url_to_path(url)
        if path and path.exists():
            return path.read_bytes(), path.suffix.lstrip(".").lower() or "png", None
        return None, None, f"로컬 파일 없음: {path}"

    # HTTP(S) → httpx 다운로드
    if not url.startswith(("http://", "https://")):
        return None, None, f"지원 안 하는 URL: {url[:40]}"

    referer = "/".join(url.split("/")[:3]) + "/"
    for i in range(retries + 1):
        try:
            h = dict(_HEADERS_LIST[i % len(_HEADERS_LIST)])
            h["Referer"] = referer
            r = httpx.get(url, headers=h, timeout=timeout,
                          follow_redirects=True, verify=False)
            if r.status_code == 200 and len(r.content) > 200:
                # 확장자: URL의 확장자 or content-type
                ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
                if ext not in ("jpg", "jpeg", "png", "webp", "avif", "gif"):
                    ct = r.headers.get("content-type", "")
                    ext = ct.split("/")[-1].split(";")[0] or "jpg"
                    ext = ext.replace("jpeg", "jpg")
                return r.content, ext, None
        except Exception as e:
            if i == retries:
                return None, None, f"네트워크 오류: {e.__class__.__name__}"
    return None, None, f"HTTP 실패 (최종 상태: {getattr(r, 'status_code', '?')})"


def main():
    ap = argparse.ArgumentParser(description="고화질 이미지 일괄 다운로드 → ZIP")
    ap.add_argument("json_path", help="line_matrix.html에서 내려받은 백업 JSON 경로")
    ap.add_argument("--out", help="출력 ZIP 경로 (기본: <json>_hires.zip)")
    ap.add_argument("--workers", type=int, default=10, help="병렬 다운로드 수 (기본 10)")
    args = ap.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"❌ 파일 없음: {json_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not items:
        print("❌ JSON의 items 배열이 비어있습니다", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out) if args.out else \
        json_path.with_name(json_path.stem + "_hires.zip")

    print(f"📥 입력: {json_path.name}")
    print(f"📦 출력: {out_path.name}")
    print(f"🔢 항목: {len(items)}건 · 병렬: {args.workers}")
    print(f"⏳ 다운로드 시작...\n")

    # 병렬 다운로드
    results: list[tuple[int, dict, bytes | None, str | None, str | None]] = [None] * len(items)

    def process(idx_item):
        i, it = idx_item
        url = it.get("image_hires") or it.get("image_url") or it.get("image_thumb") or ""
        content, ext, err = fetch_image(url)
        return i, it, content, ext, err

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process, (i, it)): i for i, it in enumerate(items)}
        done_n = 0
        for fut in as_completed(futures):
            i, it, content, ext, err = fut.result()
            results[i] = (i, it, content, ext, err)
            done_n += 1
            if done_n % 20 == 0 or done_n == len(items):
                print(f"  [{done_n}/{len(items)}] 진행 중...")

    # ZIP 쓰기
    ok_n = 0
    fallback_n = 0
    fail_n = 0
    manifest_rows = [[
        "순번", "id", "브랜드", "라인", "탭", "핏", "소분류",
        "상품명", "상품URL", "이미지파일", "ST마크", "원본URL", "상태",
    ]]

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, it, content, ext, err in results:
            brand = it.get("brand", "")
            name = it.get("name", "")
            tab = it.get("tab", "")
            if content:
                safe = safe_filename(f"{brand}_{name}")
                fname = f"{i+1:04d}_{safe_filename(tab, 20)}_{safe}.{ext or 'jpg'}"
                zf.writestr(fname, content)
                size_kb = len(content) // 1024
                if err:  # data URL 폴백 case
                    fallback_n += 1
                    status = f"폴백 ({size_kb}KB)"
                    print(f"  [{i+1:>4}] ⚠ {name[:50]} — 폴백 썸네일 ({size_kb}KB)")
                else:
                    ok_n += 1
                    status = f"OK ({size_kb}KB)"
                    if size_kb > 100:
                        print(f"  [{i+1:>4}] ✓ {name[:50]} ({size_kb}KB)")
            else:
                fail_n += 1
                fname = ""
                status = f"실패: {err}"
                print(f"  [{i+1:>4}] ✗ {name[:50]} — {err}")

            manifest_rows.append([
                i + 1, it.get("id", ""), brand, it.get("line", ""), tab,
                it.get("fit", ""), it.get("sub", ""), name,
                it.get("product_url", ""), fname,
                it.get("st_mark", ""), it.get("image_hires", "")[:200],
                status,
            ])

        # manifest.csv (UTF-8 BOM for Excel)
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerows(manifest_rows)
        zf.writestr("manifest.csv", "\ufeff" + buf.getvalue())

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"\n✅ 완료 — {out_path}")
    print(f"   크기: {size_mb:.1f}MB")
    print(f"   원본 해상도 성공: {ok_n}건")
    if fallback_n:
        print(f"   폴백 (썸네일만): {fallback_n}건 — 원본 URL 미지정 또는 data URL")
    if fail_n:
        print(f"   실패: {fail_n}건 — manifest.csv의 상태 컬럼 확인")


if __name__ == "__main__":
    main()
