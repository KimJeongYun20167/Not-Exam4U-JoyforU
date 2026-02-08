import re
import random
import streamlit as st

st.set_page_config(page_title="이제 호그와트로!", layout="centered")
def set_background(image_url: str):
    st.markdown(
        f"""
        <style>
        /* 배경 */
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }}

        /* 어두운 오버레이 */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.75);
            z-index: 0;
        }}

        /* 모든 컨텐츠를 위로 */
        .block-container {{
            position: relative;
            z-index: 1;
            max-width: 720px;
        }}

        /* 제목 */
        h1 {{
            color: white;
            font-weight: 900;
        }}
        h2, h3, p, label, div {{
            color: white !important;
        }}

        /* textarea */
        textarea {{
            background: rgba(0,0,0,0.55) !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
        }}

        /* 기본 버튼 */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 800;
            padding: 10px;
        }}

        /* 슬리데린 초록 버튼 (문제 생성) */
        button[kind="primary"] {{
            background-color: #1f6f43 !important;
            color: white !important;
            border: none !important;
        }}

        /* 보조 버튼 */
        .stButton > button:not([kind="primary"]) {{
            background: transparent !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.6) !important;
        }}

        /* info / success 박스도 검정 투명 */
        div[data-testid="stAlert"] {{
            background: rgba(0,0,0,0.55) !important;
            color: white !important;
            border-radius: 10px;
        }}

        /* ✅ 모바일에서 제목 한 줄로 */
        @media (max-width: 480px) {{
          h1 {{
            font-size: 26px !important;
            line-height: 1.1 !important;
            margin-bottom: 6px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            max-width: 100% !important;
          }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 🔮 배경 이미지
set_background(
    "https://raw.githubusercontent.com/KimJeongYun20167/Not-Exam4U-JoyforU/main/IMG_5661.jpeg"
)

# ---------------- 출제 로직 ----------------
MARKS = ["①", "②", "③", "④", "⑤"]
ANS = ["1", "2", "3", "4", "5"]

def split_sentences(text):
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sents if s]

def make_problem(text):
    sents = split_sentences(text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아."

    idx = random.randrange(0, len(sents))
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx+1:]

    k = len(remaining)
    correct_pos = min(max(idx, 1), k)

    positions = list(range(1, k+1))
    while len(positions) < 5:
        positions.append(k)
    positions = positions[:5]

    answer = str(positions.index(correct_pos) + 1)

    out = []
    for i in range(len(remaining)+1):
        if i in positions:
            out.append(f"({MARKS[positions.index(i)]})")
        if i < len(remaining):
            out.append(remaining[i])

    return {
        "insert": insert_sent,
        "passage": " ".join(out),
        "answer": answer
    }, None

# ---------------- 상태 ----------------
for k, v in {
    "prob": None,
    "show_answer": False,
    "text": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- UI ----------------
st.title("🪄 이제 호그와트로!")
st.caption("Not EXAM4YOU, Joy for U")

st.text_area("지문 입력", key="text", height=180)

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("문제 생성", type="primary"):
        p, e = make_problem(st.session_state.text)
        if e:
            st.error(e)
        else:
            st.session_state.prob = p
            st.session_state.show_answer = False
with c2:
    if st.button("정답 보기"):
        st.session_state.show_answer = True
with c3:
    if st.button("새 지문"):
        st.session_state.prob = None
        st.session_state.text = ""
        st.session_state.show_answer = False

if st.session_state.prob:
    st.info(st.session_state.prob["insert"])
    st.write(st.session_state.prob["passage"])
    if st.session_state.show_answer:
        st.success(st.session_state.prob["answer"])
