#!/usr/bin/env python3
"""스캔·비트맵 폰트 PDF를 macOS Vision OCR로 읽어 data/raw/<id>.json 생성

extract_pdf.py 로 글자가 깨지는 옛 PDF(예: 1997년 LSTM 논문)에만 사용한다.

사용법:
    .venv/bin/python ocr_pdf.py data/pdf/lstm.pdf --id lstm --pages 1-12
"""
import argparse
import json
import re
from pathlib import Path

import pymupdf
import Quartz
import Vision

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
HEADING_RE = re.compile(r"^(\d+(\.\d+)*\.?\s+\S|ABSTRACT$|Abstract$|References$|REFERENCES$)", re.I)


def ocr_page(page, dpi=400):
    pix = page.get_pixmap(dpi=dpi)
    data = pix.tobytes("png")
    src = Quartz.CGImageSourceCreateWithData(
        Quartz.CFDataCreate(None, data, len(data)), None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setUsesLanguageCorrection_(True)
    req.setRecognitionLanguages_(["en-US"])
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    ok, err = handler.performRequests_error_([req], None)
    if not ok:
        raise RuntimeError(f"OCR 실패: {err}")
    lines = []
    for obs in req.results() or []:
        cand = obs.topCandidates_(1)
        if not cand:
            continue
        box = obs.boundingBox()
        # Vision 좌표는 좌하단 원점 + 정규화 → 위→아래, 왼→오른쪽 정렬용 키로 변환
        x, y = box.origin.x, box.origin.y
        lines.append((round(1 - y, 3), round(x, 3), cand[0].string()))
    # 2단 조판 대응: 왼쪽 단 먼저, 각 단은 위→아래
    lines.sort(key=lambda t: (1 if t[1] > 0.48 else 0, t[0]))
    return [t[2] for t in lines]


def clean_join(lines):
    """OCR 줄 목록 → 단락 목록. 빈 줄이 없으므로 문장부호와 들여쓰기로 나눈다."""
    paras, buf = [], []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        heading = bool(HEADING_RE.match(s)) and len(s) < 90
        if heading:
            if buf:
                paras.append((" ".join(buf), False)); buf = []
            paras.append((s, True))
            continue
        if buf and re.search(r"[.!?:\"”)\]]$", buf[-1]) and re.match(r"^[A-Z(\[“\"]", s):
            paras.append((" ".join(buf), False)); buf = []
        buf.append(s)
    if buf:
        paras.append((" ".join(buf), False))
    out = []
    for text, heading in paras:
        text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
        text = re.sub(r"\s+", " ", text).strip()
        if heading or len(text) >= 25:
            out.append({"text": text, "heading": heading})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--id", required=True)
    ap.add_argument("--pages", default="", help="예: 1-12 (기본: 전체)")
    ap.add_argument("--dpi", type=int, default=400)
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    if a.pages:
        lo, _, hi = a.pages.partition("-")
        rng = range(int(lo) - 1, int(hi or lo))
    else:
        rng = range(len(doc))

    all_paras = []
    for pno in rng:
        lines = ocr_page(doc[pno], a.dpi)
        for p in clean_join(lines):
            p["page"] = pno + 1
            all_paras.append(p)
        print(f"  p.{pno+1}: {len(lines)}줄")

    for i, p in enumerate(all_paras, 1):
        p["n"] = f"p{i:03d}"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{a.id}.json").write_text(
        json.dumps({"id": a.id, "source": Path(a.pdf).name + " (OCR)", "paragraphs": all_paras},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (RAW_DIR / f"{a.id}.txt").write_text(
        "\n\n".join(f"[{p['n']}] {'#' if p['heading'] else ' '} (p.{p['page']}) {p['text']}"
                    for p in all_paras), encoding="utf-8")
    print(f"✅ {a.id}: {len(all_paras)}개 단락 → data/raw/{a.id}.json / .txt")


if __name__ == "__main__":
    main()
