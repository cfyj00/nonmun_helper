"""논문읽기 도우미 — 딥러닝/머신러닝/인공지능 필독 논문 읽기 앱"""

import json
import os
import streamlit as st
from pathlib import Path

# ─── 페이지 설정 ───
st.set_page_config(
    page_title="논문읽기 도우미",
    page_icon="📖",
    layout="centered",
)

# ─── 데이터 로드 ───
DATA_PATH = Path(__file__).parent / "papers.json"

@st.cache_data
def load_papers():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["papers"]

papers = load_papers()

# ─── 상태 관리 ───
if "current_paper_idx" not in st.session_state:
    st.session_state.current_paper_idx = 0
if "current_section_idx" not in st.session_state:
    st.session_state.current_section_idx = 0
if "completed" not in st.session_state:
    st.session_state.completed = set()

# ─── 헬퍼 함수 ───
def get_progress():
    """전체 진행률 계산"""
    total = sum(len(p["sections"]) for p in papers)
    return len(st.session_state.completed) / total * 100

def get_current_paper():
    return papers[st.session_state.current_paper_idx]

def get_current_section():
    paper = get_current_paper()
    return paper["sections"][st.session_state.current_section_idx]

def mark_completed(paper_id, section_id):
    st.session_state.completed.add(f"{paper_id}:{section_id}")

# ─── 사이드바 ───
with st.sidebar:
    st.title("📖 논문읽기 도우미")
    st.markdown("---")

    # 진행률
    progress = get_progress()
    st.subheader("진행률")
    st.progress(progress / 100)
    total = sum(len(p["sections"]) for p in papers)
    done = len(st.session_state.completed)
    st.caption(f"{done}/{total} 단락 완료 ({progress:.0f}%)")

    st.markdown("---")

    # 논문 선택
    st.subheader("논문 선택")
    paper_names = [f"{i+1}. {p['category']} — {p['title'][:40]}..." for i, p in enumerate(papers)]
    selected = st.selectbox("읽을 논문 선택", paper_names, 
                            index=st.session_state.current_paper_idx,
                            key="paper_select")
    idx = paper_names.index(selected)
    if idx != st.session_state.current_paper_idx:
        st.session_state.current_paper_idx = idx
        st.session_state.current_section_idx = 0

    st.markdown("---")

    # 논문별 완료 현황
    st.subheader("논문별 현황")
    for i, p in enumerate(papers):
        p_total = len(p["sections"])
        p_done = sum(1 for s in p["sections"] if f"{p['id']}:{s['paragraph_id']}" in st.session_state.completed)
        st.progress(p_done / p_total)
        status = "✅ 완료" if p_done == p_total else f"{p_done}/{p_total}"
        st.caption(f"{p['title'][:30]}... — {status}")

    st.markdown("---")
    
    # 초기화 버튼
    if st.button("🔄 전체 초기화", type="secondary"):
        st.session_state.current_paper_idx = 0
        st.session_state.current_section_idx = 0
        st.session_state.completed = set()
        st.rerun()

# ─── 메인 콘텐츠 ───
paper = get_current_paper()
section = get_current_section()

#论文헤더
st.title(f"📄 {paper['title']}")
st.markdown(f"**{paper['authors']}** | {paper['year']} | {paper['venue']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"📌 분야: {paper['category_ko']}")
with col2:
    st.info(f"🆔 arXiv: {paper['arxiv']}")
with col3:
    st.warning(f"⭐ 왜必读: {paper['why_must_read']}")

st.markdown("---")

# 진행 바 (论文 내 section별)
current_p = st.session_state.current_section_idx
total_s = len(paper["sections"])
st.progress((current_p + 1) / total_s)
st.caption(f"📑 {paper['title']} — {current_p + 1}/{total_s} 단락")

# 단락 제목
st.markdown(f"### 📖 오늘 읽을 단락: {section['title']}")
st.markdown("")

# 1. 단락 구조
with st.expander("🔍 1. 단락 구조 — 이 단락의 논리 흐름", expanded=True):
    for i, point in enumerate(section["structure"], 1):
        st.write(f"**{i}.** {point}")

# 2. 핵심 개념
with st.expander("📚 2. 핵심 개념 — 이해에 필요한 용어", expanded=True):
    for term, desc in section["key_concepts"].items():
        st.markdown(f"**`{term}`**: {desc}")

# 3. 요약
with st.expander("📝 3. 요약 — 이 단락의 핵심 내용", expanded=True):
    st.write(section["summary"])

st.markdown("---")

# 4. 원문
with st.container():
    st.markdown("### 🔎 4. 원문")
    st.markdown('---')
    st.info(section["paragraph_text"])

st.markdown("---")

# 액션 영역
action_col1, action_col2 = st.columns([1, 1])

with action_col1:
    if st.button("✅ 이 단락 읽음 → 다음 단락", type="primary", use_container_width=True):
        mark_completed(paper["id"], section["paragraph_id"])
        if st.session_state.current_section_idx < len(paper["sections"]) - 1:
            st.session_state.current_section_idx += 1
        else:
            # 이论文 끝 → 다음论文
            if st.session_state.current_paper_idx < len(papers) - 1:
                st.session_state.current_paper_idx += 1
                st.session_state.current_section_idx = 0
        st.rerun()

with action_col2:
    if st.button("📌 이 단락 저장", use_container_width=True):
        st.success("이 단락을 스크랩했습니다. 나중에 다시 읽어보세요!")

# 하단 안내
st.markdown("---")
st.info("""
💡 **읽기 가이드**
1. 먼저 **단락 구조**를 읽어보세요 — 이 단락이 어떤 논리로 구성되어 있는지 파악합니다.
2. **핵심 개념**을 확인하세요 — 낯선 용어를 미리 알아두면 원문이 훨씬 수월합니다.
3. **요약**을 먼저 읽고 원문을 보세요 — 미리 대체한다는 느낌보다, 직접 읽으며 확인한다는 느낌으로 접근하세요.
4. 원문을 다 읽은 후 → **"읽음" 버튼**을 눌러 다음 단락으로 넘어갑니다.
5.わからない 것이 있으면 바로 질문하세요!
""")

# 완료 시
if get_progress() >= 100:
    st.balloons()
    st.success("🎉 축하합니다! 모든 필독 논문을 완료했습니다!")
