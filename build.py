#!/usr/bin/env python3
"""data/*.json (논문별 해석·주석) + data/raw/*.json (PDF 추출 원문) + template.html → index.html

사용법:
    python3 build.py                     빌드 (index.html, papers.json 생성)
    python3 build.py --split <id> p012   raw 단락을 문장 단위로 쪼개 번호와 함께 출력 (해석 작성용)
    python3 build.py --check             빌드 없이 검증만

data/<id>.json 의 단락(section) 형식 — 둘 중 하나:
    (A) "src": "p012", "sentences_ko": [{"ko": "...", "note": "..."}, ...]
        → 원문 영어는 data/raw/<id>.json 의 p012 에서 가져와 문장으로 분리하고, 해석을 순서대로 붙임
    (B) "sentences": [{"en": "...", "ko": "...", "note": "..."}, ...]
        → 영어까지 직접 지정 (raw 가 없거나 분리 결과를 손봐야 할 때)
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
TEMPLATE = ROOT / "template.html"
OUT_HTML = ROOT / "index.html"
OUT_JSON = ROOT / "papers.json"
TOKEN = "/*__PAPERS_JSON__*/[]"

REQUIRED_PAPER = ["id", "order", "title", "authors", "year", "venue", "arxiv",
                  "category", "category_ko", "why_must_read", "sections"]
REQUIRED_SECTION = ["paragraph_id", "title", "structure", "key_concepts", "summary"]

ABBREVIATIONS = ["et al.", "e.g.", "i.e.", "cf.", "vs.", "resp.", "approx.", "w.r.t.",
                 "Fig.", "Figs.", "Eq.", "Eqs.", "Sec.", "Secs.", "Tab.", "No.", "Vol.",
                 "Dr.", "Mr.", "Ms.", "Prof.", "etc.", "al."]


def fail(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def split_sentences(text: str):
    """논문 문장 분리기. 약어·소수점·괄호 안 마침표를 보호한 뒤 [.!?] + 공백 + 대문자/기호 에서 분리."""
    t = text
    for ab in ABBREVIATIONS:
        t = t.replace(ab, ab.replace(".", "\x00"))
    t = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + "\x00" + m.group(2), t)   # 3.5, 0.1
    t = re.sub(r"\b([A-Z])\.\s", lambda m: m.group(1) + "\x00 ", t)           # 이니셜 "J. Smith"
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[“\"‘'0-9])", t)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def load_raw(pid):
    path = RAW_DIR / f"{pid}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {p["n"]: p for p in data["paragraphs"]}


def resolve_sentences(pid, s, raw, where):
    if "sentences" in s and s["sentences"]:
        sents = s["sentences"]
        for j, x in enumerate(sents):
            if not x.get("en") or not x.get("ko"):
                fail(f"{where}: 문장 {j+1} en/ko 누락")
            x.setdefault("note", "")
        return sents
    if "src" not in s:
        fail(f"{where}: 'src' 또는 'sentences' 가 필요합니다")
    if raw is None:
        fail(f"{where}: data/raw/{pid}.json 이 없습니다 (extract_pdf.py 먼저 실행)")
    srcs = s["src"] if isinstance(s["src"], list) else [s["src"]]
    en_list = []
    for n in srcs:
        if n not in raw:
            fail(f"{where}: raw 단락 {n} 없음")
        en_list += split_sentences(raw[n]["text"])
    # from/to: 앞뒤 군더더기(저자 정보·각주 등) 잘라내기. 문장 앞부분 문자열로 지정.
    if s.get("from"):
        i = next((k for k, e in enumerate(en_list) if e.startswith(s["from"])), None)
        if i is None:
            fail(f"{where}: 'from' 으로 시작하는 문장을 찾지 못함 — {s['from']!r}")
        en_list = en_list[i:]
    if s.get("to"):
        i = next((k for k, e in enumerate(en_list) if e.startswith(s["to"])), None)
        if i is None:
            fail(f"{where}: 'to' 로 시작하는 문장을 찾지 못함 — {s['to']!r}")
        en_list = en_list[:i + 1]
    if s.get("drop"):
        en_list = [e for k, e in enumerate(en_list) if k + 1 not in s["drop"]]
    # fix: PDF 추출 오류(머리말 붙음, 하이픈 깨짐 등) 난 문장을 통째로 교체.
    # {"1": "올바른 문장"} 또는 {"1": ["문장 A", "문장 B"]} (한 문장을 여러 개로 쪼갤 때)
    for k in sorted((s.get("fix") or {}), key=lambda x: -int(x)):
        v = s["fix"][k]
        i = int(k) - 1
        if not (0 <= i < len(en_list)):
            fail(f"{where}: fix 인덱스 {k} 범위를 벗어남 (문장 {len(en_list)}개)")
        en_list[i:i + 1] = v if isinstance(v, list) else [v]
    ko_list = s.get("sentences_ko") or []
    if len(ko_list) != len(en_list):
        print(f"\n--- {where} 문장 분리 결과 ({len(en_list)}문장) ---", file=sys.stderr)
        for i, e in enumerate(en_list, 1):
            print(f"  [{i}] {e}", file=sys.stderr)
        fail(f"{where}: 영어 {len(en_list)}문장 vs 해석 {len(ko_list)}개 — 개수가 맞지 않습니다")
    return [{"en": e, "ko": k["ko"], "note": k.get("note", "")} for e, k in zip(en_list, ko_list)]


def load_papers():
    papers = []
    for path in sorted(glob.glob(str(DATA_DIR / "*.json"))):
        try:
            p = json.loads(Path(path).read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{path}: JSON 오류 — {e}")
        for k in REQUIRED_PAPER:
            if k not in p:
                fail(f"{path}: 논문 필드 누락 '{k}'")
        raw = load_raw(p["id"])
        seen = set()
        out_sections = []
        for i, s in enumerate(p["sections"]):
            where = f"{p['id']} 단락 {i+1} ({s.get('paragraph_id','?')})"
            for k in REQUIRED_SECTION:
                if k not in s:
                    fail(f"{where}: 필드 누락 '{k}'")
            if s["paragraph_id"] in seen:
                fail(f"{where}: paragraph_id 중복")
            seen.add(s["paragraph_id"])
            if not s["key_concepts"]:
                fail(f"{where}: key_concepts 비어 있음")
            sents = resolve_sentences(p["id"], s, raw, where)
            out_sections.append({
                "paragraph_id": s["paragraph_id"],
                "title": s["title"],
                "sentences": sents,
                "paragraph_text": " ".join(x["en"] for x in sents),
                "structure": s["structure"],
                "key_concepts": s["key_concepts"],
                "summary": s["summary"],
            })
        p["sections"] = out_sections
        papers.append(p)
    papers.sort(key=lambda p: p["order"])
    ids = [p["id"] for p in papers]
    if len(ids) != len(set(ids)):
        fail("논문 id 중복")
    return papers


def cmd_split(pid, ns):
    raw = load_raw(pid)
    if raw is None:
        fail(f"data/raw/{pid}.json 없음")
    for n in ns:
        if n not in raw:
            fail(f"{pid} 에 {n} 없음")
        print(f"### {n} (p.{raw[n]['page']})")
        for i, e in enumerate(split_sentences(raw[n]["text"]), 1):
            print(f"[{i}] {e}")
        print()


def main():
    args = sys.argv[1:]
    if args[:1] == ["--split"]:
        cmd_split(args[1], args[2:])
        return
    papers = load_papers()
    n_sec = sum(len(p["sections"]) for p in papers)
    n_sent = sum(len(s["sentences"]) for p in papers for s in p["sections"])
    if args[:1] == ["--check"]:
        print(f"✅ 검증 통과: 논문 {len(papers)}편, 단락 {n_sec}개, 문장 {n_sent}개")
        return
    template = TEMPLATE.read_text(encoding="utf-8")
    if TOKEN not in template:
        fail(f"template.html 에 토큰 {TOKEN} 이 없습니다")
    payload = json.dumps(papers, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    OUT_HTML.write_text(template.replace(TOKEN, payload), encoding="utf-8")
    OUT_JSON.write_text(json.dumps({"papers": papers}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 빌드 완료: 논문 {len(papers)}편, 단락 {n_sec}개, 문장 {n_sent}개")
    print(f"   → {OUT_HTML.name} ({OUT_HTML.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
