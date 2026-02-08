import re
import random
import streamlit as st

st.set_page_config(page_title="이제 호그와트로!", layout="centered")

# ---------------- 배경 + 가독성 CSS ----------------
def set_background(image_url: str):
    st.markdown(
        f"""
        <style>
        /* 배경 이미지 */
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 어두운 오버레이(가독성 핵심) */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.70);  /* 더 어둡게 */
            z-index: 0;
        }}

        /* 전체 컨텐츠를 오버레이 위로 */
        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 20px;
            padding-bottom: 24px;
            max-width: 760px;
        }}

        /* 헤더 카드 */
        .header-card {{
            background: #FFFFFF;          /* 완전 불투명 */
            border-radius: 18px;
            padding: 16px 16px 14px 16px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.35);
            margin-bottom: 12px;
        }}

        .title {{
            font-size: 36px;
            font-weight: 900;
            line-height: 1.05;
            margin: 0;
            color: #111;
        }}
        .subtitle {{
            margin-top: 8px;
            color: #555;
            font-size: 15px;
            font-weight: 600;
        }}

        /* 입력/본문 카드 */
        .card {{
            background: #FFFFFF;          /* 완전 불투명 */
            border-radius: 18px;
            padding: 14px 14px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.35);
            margin-top: 10px;
        }}

        /* 지문/문장 표시(텍스트 가독성) */
        .passage {{
            color: #111;
            font-size: 16px;
            line-height: 1.75;
            word-break: break-word;
        }}

        /* Streamlit 기본 alert(삽입문장)도 카드 톤으로 */
        div[data-testid="stAlert"] {{
            border-radius: 14px !important;
        }}

        /* textarea 둥글게 */
        textarea {{
            border-radius: 14px !important;
        }}

        /* 버튼 둥글고 안정감 */
        .stButton>button {{
            border-radius: 14px !important;
            padding: 10px 12px !important;
            font-weight: 800 !important;
        }}

        /* 모바일: 타이틀 조금 줄이기 */
        @media (max-width: 480px) {{
            .title {{ font-size: 30px; }}
            .passage {{ font-size: 15px; }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ 너의 raw 이미지 URL
BG_URL = "https://raw.githubusercontent.com/KimJeongYun20167/Not-Exam4U-JoyforU/main/IMG_5661.jpeg"
set_background(BG_URL)

# ---------------- 출제 로직 ----------------
MARKS = ["①", "②", "③", "④", "⑤"]
ANS = ["1", "2", "3", "4", "5"]

def split_sentences(text: str):
    t = text.strip()
    if not t:
        return []
    sents = re.split(r"(?<=[.!?])\s+", t)
    return [s for s in sents if len(s.strip()) >= 2]

def pick_random_sentence_index(sentences):
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def render_with_marks(remaining, positions_for_marks):
    pos2labels = {}
    for j, pos in enumerate(positions_for_marks):
        pos2labels.setdefault(pos, []).append(MARKS[j])

    out = []
    for i in range(len(remaining) + 1):
        if i in pos2labels:
            out.append("".join([f"({lab})" for lab in pos2labels[i]]))
        if i < len(remaining):
            out.append(remaining[i])
    return " ".join(out)

def choose_mark_positions(k, correct_pos):
    if k <= 0:
        return [0, 0, 0, 0, 0]

    boundaries = list(range(1, k + 1))  # 1..k

    if k >= 5:
        min_start = 1
        max_start = k - 4
        start_low = max(min_start, correct_pos - 4)
        start_high = min(max_start, correct_pos)
        start = random.randint(start_low, start_high) if start_low <= start_high else random.randint(min_start, max_start)
        return list(range(start, start + 5))

    pos = boundaries[:]
    while len(pos) < 5:
        pos.append(k)  # 짧으면 뒤로 몰아넣기
    return pos[:5]

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아(문장 2개 이상 필요)."

    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)
    correct_pos = min(max(idx, 1), k)

    mark_positions = choose_mark_positions(k, correct_pos)
    answer_index = mark_positions.index(correct_pos)
    answer_plain = ANS[answer_index]

    passage_with_marks = render_with_marks(remaining, mark_positions)

    return {
        "insert_sentence": insert_sent.strip(),
        "passage_with_marks": passage_with_marks,
        "answer_plain": answer_plain,
    }, None

# ---------------- 상태 ----------------
for key, default in {
    "prob": None,
    "show_answer": False,
    "show_input": True,
    "passage_text": "",
    "error_msg": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------- 콜백 ----------------
def on_generate():
    prob, err = make_problem(st.session_state.get("passage_text", ""))
    if err:
        st.session_state.prob = None
        st.session_state.show_answer = False
        st.session_state.show_input = True
        st.session_state.error_msg = err
        return
    st.session_state.prob = prob
    st.session_state.show_answer = False
    st.session_state.show_input = False
    st.session_state.passage_text = ""
    st.session_state.error_msg = ""

def on_show_answer():
    if st.session_state.prob is not None:
        st.session_state.show_answer = True

def on_new_passage():
    st.session_state.prob = None
    st.session_state.show_answer = False
    st.session_state.show_input = True
    st.session_state.passage_text = ""
    st.session_state.error_msg = ""

# ---------------- UI ----------------
st.markdown(
    """
    <div class="header-card">
      <p class="title">🪄 이제 호그와트로!</p>
      <div class="subtitle">너무 졸리다</div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.error_msg:
    st.error(st.session_state.error_msg)

st.markdown('<div class="card">', unsafe_allow_html=True)

if st.session_state.show_input:
    st.text_area("지문 입력", key="passage_text", height=180)

c1, c2, c3 = st.columns(3)
with c1:
    st.button("문제 생성", type="primary", on_click=on_generate, use_container_width=True)
with c2:
    st.button("정답 보기", on_click=on_show_answer, use_container_width=True)
with c3:
    st.button("새 지문", on_click=on_new_passage, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# 출력은 '완전 흰 카드' 안에 넣어서 배경 영향 0으로 만들기
if st.session_state.prob is not None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info(st.session_state.prob["insert_sentence"])
    st.markdown(f'<div class="passage">{st.session_state.prob["passage_with_marks"]}</div>', unsafe_allow_html=True)

    if st.session_state.show_answer:
        st.success(st.session_state.prob["answer_plain"])
    st.markdown("</div>", unsafe_allow_html=True)
