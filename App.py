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
            padding-bottom: 28px;
        }}

        /* 글씨 흰색 */
        h1 {{
            color: white;
            font-weight: 900;
        }}
        h2, h3, p, label, div, span {{
            color: white !important;
        }}

        /* 입력창: 어두운 톤 */
        textarea {{
            background: rgba(0,0,0,0.55) !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.35) !important;
        }}

        /* 버튼 */
        .stButton > button {{
            border-radius: 10px !important;
            font-weight: 800 !important;
            padding: 10px 12px !important;
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

        /* info/success 박스 */
        div[data-testid="stAlert"] {{
            background: rgba(0,0,0,0.55) !important;
            color: white !important;
            border-radius: 10px !important;
        }}

        /* 모바일: 제목 한 줄 유지(넘치면 …) */
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

set_background(
    "https://raw.githubusercontent.com/KimJeongYun20167/Not-Exam4U-JoyforU/main/IMG_5661.jpeg"
)

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

def choose_mark_positions(k, correct_pos):
    """
    표식 위치는 '정답 포함 연속 5개 경계' (기존 방식 유지)
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

    boundaries = list(range(1, k + 1))
    pos = boundaries[:]
    while len(pos) < 5:
        pos.append(k)
    return pos[:5]

def render_with_marks(remaining, positions_for_marks):
    """
    ✅ 핵심: 지문 '뒤에서부터' ⑤,④,③,②,① 붙이기
    - 가장 뒤(마지막에 가까운) 표식이 (⑤)
    - 그 앞이 (④) ... 이런 식
    """
    pos2labels = {}

    # positions_for_marks는 보통 오름차순.
    # 뒤에서부터 순회하면서 ⑤부터 붙인다.
    for rank_from_end, pos in enumerate(sorted(positions_for_marks, reverse=True)):
        label = MARKS[4 - rank_from_end]  # 0->⑤, 1->④, 2->③, 3->②, 4->①
        pos2labels.setdefault(pos, []).append(label)

    out = []
    for i in range(len(remaining) + 1):
        if i in pos2labels:
            out.append("".join([f"({lab})" for lab in pos2labels[i]]))
        if i < len(remaining):
            out.append(remaining[i])

    return " ".join(out)

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아(문장 2개 이상 필요)."

    idx = pick_random_sentence_index(sents)

    # 삽입 문장 1개 뽑고 제거
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)

    # 정답 경계(1..k)
    correct_pos = min(max(idx, 1), k)

    mark_positions = choose_mark_positions(k, correct_pos)

    # ✅ 핵심: 표식 번호가 '뒤에서부터 ⑤..①'이므로 정답도 뒤집어서 계산
    rank_from_start = mark_positions.index(correct_pos)  # 0..4 (앞에서 몇 번째 표식 위치인지)
    answer_plain = str(5 - rank_from_start)             # 0->5, 1->4, 2->3, 3->2, 4->1

    passage_with_marks = render_with_marks(remaining, mark_positions)

    return {
        "insert_sentence": insert_sent.strip(),
        "passage_with_marks": passage_with_marks,
        "answer_plain": answer_plain,
    }, None

# ---------------- 상태(입력 숨김/삭제 기능 유지) ----------------
if "prob" not in st.session_state:
    st.session_state["prob"] = None
if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False
if "show_input" not in st.session_state:
    st.session_state["show_input"] = True
if "passage_text" not in st.session_state:
    st.session_state["passage_text"] = ""
if "error_msg" not in st.session_state:
    st.session_state["error_msg"] = ""

# ---------------- 콜백 ----------------
def on_generate():
    text = st.session_state.get("passage_text", "")
    prob, err = make_problem(text)

    if err:
        st.session_state["prob"] = None
        st.session_state["show_answer"] = False
        st.session_state["show_input"] = True
        st.session_state["error_msg"] = err
        return

    st.session_state["prob"] = prob
    st.session_state["show_answer"] = False
    st.session_state["show_input"] = False     # 입력창 숨김
    st.session_state["passage_text"] = ""      # 입력 내용 삭제
    st.session_state["error_msg"] = ""

def on_show_answer():
    if st.session_state.get("prob") is not None:
        st.session_state["show_answer"] = True

def on_new_passage():
    st.session_state["prob"] = None
    st.session_state["show_answer"] = False
    st.session_state["show_input"] = True
    st.session_state["passage_text"] = ""
    st.session_state["error_msg"] = ""

# ---------------- UI ----------------
st.title("🪄 이제 호그와트로!")
st.caption("Not EXAM4YOU. Joy for you")

if st.session_state["error_msg"]:
    st.error(st.session_state["error_msg"])

if st.session_state["show_input"]:
    st.text_area("지문 입력", key="passage_text", height=180)

c1, c2, c3 = st.columns(3)
with c1:
    st.button("문제 생성", type="primary", on_click=on_generate, use_container_width=True)
with c2:
    st.button("정답 보기", on_click=on_show_answer, use_container_width=True)
with c3:
    st.button("새 지문", on_click=on_new_passage, use_container_width=True)

if st.session_state["prob"] is not None:
    st.info(st.session_state["prob"]["insert_sentence"])
    st.write(st.session_state["prob"]["passage_with_marks"])
    if st.session_state["show_answer"]:
        st.success(st.session_state["prob"]["answer_plain"])
