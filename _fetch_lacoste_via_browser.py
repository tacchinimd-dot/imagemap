"""Lacoste Akamai 우회 — Playwright non-headless 브라우저 + page.goto 사용.
(headless 모드는 Akamai가 차단, context.request도 차단 → 비쥬얼 모드 + 네비게이션만 통과)
URL에서 `impolicy=pctp`는 제거 (AVIF 응답 → JPEG 요청).
"""
from __future__ import annotations
import sys, hashlib, io, time, re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\AD0903\brand_crawler")
CACHE_DIR = ROOT / ".image_cache"
FAILED_LOG = CACHE_DIR / "failed_urls.log"
MAX_W = 260
JPEG_Q = 78


def normalize_lacoste_url(url: str) -> str:
    """impolicy=pctp 제거 → JPEG 응답."""
    url = re.sub(r"[&?]impolicy=[^&]*", "", url)
    url = url.rstrip("?&")
    return url


def process_and_save(body: bytes, out_jpg: Path) -> bool:
    try:
        img = Image.open(io.BytesIO(body))
        if img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        else:
            img = img.convert("RGB")
        if img.width > MAX_W:
            ratio = MAX_W / img.width
            img = img.resize((MAX_W, int(img.height * ratio)), Image.LANCZOS)
        img.save(out_jpg, format="JPEG", quality=JPEG_Q, optimize=True)
        return True
    except Exception as e:
        return False


def main():
    if not FAILED_LOG.exists():
        print("failed_urls.log 없음")
        return
    urls_raw = [u.strip() for u in FAILED_LOG.read_text(encoding="utf-8").splitlines() if u.strip()]
    urls = [(orig, normalize_lacoste_url(orig)) for orig in urls_raw if "lacoste.com" in orig]
    print(f"Lacoste 재다운로드: {len(urls)}건 (visible Chromium 사용, Akamai 우회)")
    if not urls:
        return

    t0 = time.time()
    ok = 0
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1200, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        for i, (orig_url, fetch_url) in enumerate(urls, 1):
            key = hashlib.md5(orig_url.encode()).hexdigest()
            out_jpg = CACHE_DIR / f"{key}.jpg"
            if out_jpg.exists() and out_jpg.stat().st_size > 500:
                ok += 1
                continue
            try:
                r = page.goto(fetch_url, timeout=15000)
                if r and r.status == 200:
                    body = r.body()
                    if len(body) > 500 and process_and_save(body, out_jpg):
                        ok += 1
                    else:
                        fail += 1
                else:
                    fail += 1
            except Exception as e:
                fail += 1
            if i % 20 == 0:
                elapsed = time.time() - t0
                eta = elapsed / i * (len(urls) - i)
                print(f"  [{i}/{len(urls)}] ok={ok} fail={fail} ({elapsed:.1f}s, ETA {eta/60:.1f}분)")

        browser.close()
    print(f"[완료] ok={ok} fail={fail} ({(time.time()-t0)/60:.1f}분)")


if __name__ == "__main__":
    main()
