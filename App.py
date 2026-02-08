import re
import random
import streamlit as st

st.set_page_config(page_title="이제 호그와트로!", layout="centered")

# ---------------- 배경 + 슬리데린 CSS ----------------
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
            padding-top: 28px;
        }}

        /* 제목 */
        h1 {{
            color: white;
            font-weight: 900;
        }}
        h2, h3, p, label, div {{
            color: white !important;
        }}

        /* ✅ 수정 1) 입력 박스 더 예쁘게(살짝 밝게) */
        textarea {{
            background: rgba(255,255,255,0.15) !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.35) !important;
        }}

        /* ✅ 수정 2) 버튼 간격 줄이기 */
        .stButton {{
            margin-top: 4px;
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

        /* ✅ 모바일에서 제목 한 줄로 + 넘치면 … 처리 */
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

def split_sentences(text: str):
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sents if s.strip()]

def render_with_marks(remaining, positions_for_marks):
    """
    positions_for_marks: 길이 5 리스트, 각 원소는 경계 인덱스 i (0..len(remaining))
    같은 위치에 표식이 여러 개면 (④)(⑤)처럼 붙여서 출력.
    """
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
    """
    k = remaining 문장 수
    - k>=5: 정답 포함 '연속 5개 경계' 블록
    - k<5: 존재하는 경계에 앞에서부터 배치하고, 남는 표식은 맨 뒤(k)에 붙임
    """
    if k <= 0:
        return [0, 0, 0, 0, 0]

    if k >= 5:
        min_start = 1
        max_start = k - 4
        start_low = max(min_start, correct_pos - 4)
        start_high = min(max_start, correct_pos)
        start = random.randint(start_low, start_high) if start_low <= start_high else random.randint(min_start, max_start)
        return list(range(start, start + 5))

    # k < 5
    boundaries = list(range(1, k + 1))
    pos = boundaries[:]
    while len(pos) < 5:
        pos.append(k)  # 맨 뒤로 몰기
    return pos[:5]

def pick_random_sentence_index(sentences):
    # 가능하면 첫/끝 피해서 랜덤
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def make_problem(text: str):
    sents = split_sentences(text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아."

    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)
    correct_pos = min(max(idx, 1), k)

    mark_positions = choose_mark_positions(k, correct_pos)

    # 정답: correct_pos가 mark_positions에서 처음 등장하는 위치(1~5)
    answer_index = mark_positions.index(correct_pos)
    answer_plain = ANS[answer_index]

    passage_with_marks = render_with_marks(remaining, mark_positions)

    return {
        "insert": insert_sent.strip(),
        "passage": passage_with_marks,
        "answer": answer_plain
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
st.caption("Not EXAM4YOU. Joy for you")

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
