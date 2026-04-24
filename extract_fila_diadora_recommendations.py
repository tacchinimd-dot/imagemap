"""
FILA / Diadora ST 추천 이미지 PNG 추출기.

line_matrix.py의 classify_st_match() 결과가 "core" 또는 "adapt"인
FILA·Diadora 상품만 필터링 → 원본 이미지 다운로드 → PNG 저장.

Diadora는 상품 상세 페이지 JSON-LD의 image 배열에서
사용자가 지정한 index를 우선 사용(diadora_still_overrides.json).

출력 구조:
  imagemap/recommendations_fila_diadora/
    ├── FILA/
    │   ├── CORE_직접부합/       (⭐ 그대로 얹을 수 있는 상품)
    │   └── ADAPT_타키니화가능/   (✨ 실루엣·디테일 참조 후 전환)
    └── Diadora/
        ├── CORE_직접부합/
        └── ADAPT_타키니화가능/

파일명: {탭_소분류}__{상품명안전버전}.png
"""
from __future__ import annotations
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image

from line_matrix import (
    _fetch_with_retry,
    classify_st_match,
    classify_tab,
    load_diadora,
    load_fila,
)
from diadora_image_audit import fetch_product_images

OUT_ROOT = Path(__file__).parent / "recommendations_fila_diadora"
DIADORA_OVERRIDES_PATH = Path(__file__).parent / "diadora_still_overrides.json"


def load_diadora_overrides() -> dict[str, int]:
    """상품명 → 이미지 index 매핑 (없으면 0 = 크롤러 기본 image_url)."""
    if not DIADORA_OVERRIDES_PATH.exists():
        return {}
    try:
        d = json.loads(DIADORA_OVERRIDES_PATH.read_text(encoding="utf-8"))
        return d.get("overrides", {}) or {}
    except Exception as e:
        print(f"  [override 로드 실패] {e}")
        return {}

# 추천 분류 라벨
ST_LABEL = {
    "core":  "CORE_직접부합",
    "adapt": "ADAPT_타키니화가능",
}

# 탭 → 한국어 레이블 (파일명 prefix용)
TAB_LABEL = {
    "outer":   "아우터",
    "polo":    "폴로",
    "tee":     "티셔츠_롱슬리브",
    "dress":   "드레스",
    "skirt":   "스커트",
    "sweat":   "맨투맨_후디",
    "sweater": "스웨터",
    "bottom":  "팬츠_쇼츠",
}

_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(s: str, maxlen: int = 80) -> str:
    """Windows 금지문자 제거 + 길이 제한."""
    s = _INVALID.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:maxlen].rstrip(". ")


def save_png(img_bytes: bytes, out_path: Path) -> bool:
    try:
        img = Image.open(io.BytesIO(img_bytes))
        # RGBA 유지(PNG 특성), 기타 모드는 RGB로 변환
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, format="PNG", optimize=True)
        return True
    except Exception as e:
        print(f"    [저장 실패] {out_path.name}: {e}")
        return False


def extract_for_brand(brand_label: str, items: list[dict], overrides: dict[str, int] | None = None) -> dict[str, int]:
    print(f"\n[{brand_label}] 후보 {len(items)}개")
    overrides = overrides or {}
    counters = {"core": 0, "adapt": 0, "skip": 0, "fail": 0, "override_used": 0}
    for it in items:
        tab = classify_tab(it)
        if not tab:
            counters["skip"] += 1
            continue
        st = classify_st_match(it, tab)
        if st not in ("core", "adapt"):
            counters["skip"] += 1
            continue

        name = it["name"]
        url = it.get("image_url") or ""

        # Diadora: override index가 지정된 상품은 JSON-LD image[index] 사용
        if brand_label == "Diadora" and name in overrides:
            idx = overrides[name]
            imgs = fetch_product_images(it["product_url"])
            if idx < len(imgs) and imgs[idx]:
                url = imgs[idx]
                counters["override_used"] += 1
            else:
                print(f"  [override 실패 — idx 범위 초과] {name} (idx={idx}, 총 {len(imgs)})")

        if not url or url.startswith("data:"):
            counters["fail"] += 1
            continue

        data = _fetch_with_retry(url, timeout=30, retries=2)
        if not data:
            counters["fail"] += 1
            print(f"  [다운로드 실패] {name}")
            continue

        tab_label = TAB_LABEL.get(tab, tab)
        sub = it.get("sub_raw") or ""
        fname_base = f"{tab_label}__{safe_name(sub) or '미분류'}__{safe_name(name)}.png"
        out_dir = OUT_ROOT / brand_label / ST_LABEL[st]
        out_path = out_dir / fname_base

        # 중복 상품명 방지 (동일 파일명이면 suffix 추가)
        if out_path.exists():
            stem = out_path.stem; i = 2
            while (alt := out_dir / f"{stem}_{i}.png").exists():
                i += 1
            out_path = alt

        if save_png(data, out_path):
            counters[st] += 1
            ov_mark = " [🔄 override]" if brand_label == "Diadora" and name in overrides else ""
            print(f"  [{st.upper():5s}] {tab_label}/{sub} · {name[:50]}{ov_mark}")

    print(f"  → CORE {counters['core']} · ADAPT {counters['adapt']} · 스킵 {counters['skip']} · 실패 {counters['fail']} · override {counters['override_used']}")
    return counters


def main():
    print("[로드]")
    fila = load_fila()
    dia  = load_diadora()
    dia_ov = load_diadora_overrides()
    if dia_ov:
        print(f"  Diadora 상품컷 오버라이드 {len(dia_ov)}건 적용 예정")

    # 기존 브랜드 폴더 전체 삭제 후 재생성 (멱등성 보장, 중복 누적 방지)
    import shutil
    for b in ("FILA", "Diadora"):
        bdir = OUT_ROOT / b
        if bdir.exists():
            shutil.rmtree(bdir)
    OUT_ROOT.mkdir(exist_ok=True)

    fc = extract_for_brand("FILA", fila)
    dc = extract_for_brand("Diadora", dia, dia_ov)

    print("\n[완료]")
    print(f"  FILA    : CORE {fc['core']} · ADAPT {fc['adapt']}")
    print(f"  Diadora : CORE {dc['core']} · ADAPT {dc['adapt']} (override {dc['override_used']}건 반영)")
    print(f"  출력 경로: {OUT_ROOT}")


if __name__ == "__main__":
    main()
