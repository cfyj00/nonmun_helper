#!/usr/bin/env python3
"""논문 PDF → 단락 목록 추출

사용법:
    .venv/bin/python extract_pdf.py data/pdf/attention.pdf --id attention
    .venv/bin/python extract_pdf.py --all          # data/pdf/*.pdf 전부 (파일명 = id)

산출물:
    data/raw/<id>.json   단락 배열 [{"n":"p001","page":1,"heading":false,"text":"..."}]
    data/raw/<id>.txt    사람이 훑어보기 좋은 미리보기 (단락 번호 + 본문)

이 단계는 원문을 "있는 그대로" 꺼내는 것만 담당한다.
어떤 단락을 읽을지, 해석·구조·개념은 data/<id>.json 에서 정한다.
"""
import argparse
import glob
import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"

HEADING_RE = re.compile(r"^(\d+(\.\d+)*\.?\s+\S|Abstract$|References$|Acknowledg|Appendix)", re.I)
ARXIV_WM_RE = re.compile(r"arXiv:\d{4}\.\d{4,5}v\d+\s+\[")


def clean(text: str) -> str:
    text = text.replace("­", "")               # soft hyphen
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)    # 줄바꿈 하이픈 연결
    text = text.replace("\n", " ")
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_noise(text: str) -> bool:
    if len(text) < 25:
        return True
    if ARXIV_WM_RE.search(text):
        return True
    letters = sum(c.isalpha() for c in text)
    if letters / max(len(text), 1) < 0.5:           # 수식·표·숫자 위주 블록
        return True
    return False


def extract(pdf_path: Path):
    doc = pymupdf.open(pdf_path)
    paras = []
    for pno, page in enumerate(doc, start=1):
        width = page.rect.width
        blocks = [b for b in page.get_text("blocks") if b[6] == 0]  # text blocks only
        # 2단 조판 대응: 왼쪽/전체폭 블록 → 오른쪽 블록 순으로, 각각 위→아래
        blocks.sort(key=lambda b: (1 if b[0] > width * 0.45 else 0, round(b[1], 1)))
        for b in blocks:
            text = clean(b[4])
            if not text:
                continue
            heading = bool(HEADING_RE.match(text)) and len(text) < 90
            if not heading and is_noise(text):
                continue
            paras.append({"page": pno, "heading": heading, "text": text})

    # 단·페이지 경계에서 끊긴 단락 이어 붙이기
    merged = []
    for p in paras:
        if merged and not merged[-1]["heading"] and not p["heading"]:
            prev = merged[-1]["text"]
            if not re.search(r"[.!?:”\")\]]$", prev) or p["text"][:1].islower():
                merged[-1]["text"] = prev + " " + p["text"]
                continue
        merged.append(p)

    for i, p in enumerate(merged, start=1):
        p["n"] = f"p{i:03d}"
    return [{"n": p["n"], "page": p["page"], "heading": p["heading"], "text": p["text"]} for p in merged]


def run(pdf_path: Path, pid: str):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    paras = extract(pdf_path)
    (RAW_DIR / f"{pid}.json").write_text(
        json.dumps({"id": pid, "source": pdf_path.name, "paragraphs": paras}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    lines = []
    for p in paras:
        tag = "#" if p["heading"] else " "
        lines.append(f"[{p['n']}] {tag} (p.{p['page']}) {p['text']}")
    (RAW_DIR / f"{pid}.txt").write_text("\n\n".join(lines), encoding="utf-8")
    print(f"✅ {pid}: {len(paras)}개 단락 → data/raw/{pid}.json / .txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--id")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.all:
        for f in sorted(glob.glob(str(ROOT / "data" / "pdf" / "*.pdf"))):
            pid = Path(f).stem
            raw = RAW_DIR / f"{pid}.json"
            if raw.exists():
                try:
                    src = json.loads(raw.read_text(encoding="utf-8")).get("source", "")
                except Exception:
                    src = ""
                if "(OCR)" in src:
                    print(f"⏭  {pid}: OCR로 추출된 파일이라 건너뜀 (ocr_pdf.py로 다시 뽑으세요)")
                    continue
            run(Path(f), pid)
    elif a.pdf:
        run(Path(a.pdf), a.id or Path(a.pdf).stem)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
