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

        /* ✅ 입력창: 예전처럼 어두운 톤(흰색 X) */
        textarea {{
            background: rgba(0,0,0,0.55) !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.35) !important;
        }}

        /* 버튼 기본 */
        .stButton > button {{
            border-radius: 10px !important;
            font-weight: 800 !important;
            padding: 10px 12px !important;
        }}

        /* ✅ 슬리데린 초록(문제 생성) */
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
    # 텍스트는 그대로 두고, 내부적으로만 문장 경계 판정
    t = text.strip()
    if not t:
        return []
    sents = re.split(r"(?<=[.!?])\s+", t)
    return [s for s in sents if len(s.strip()) >= 2]

def pick_random_sentence_index(sentences):
    # 가능하면 첫/끝 피해서 랜덤
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def render_with_marks(remaining, positions_for_marks):
    # 같은 위치에 여러 표식이면 (④)(⑤)처럼 붙여서 출력
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
    출제 표식 위치를 '항상 뒤쪽'으로 고정.
    - k>=5: 맨 뒤 5개 경계 [k-4, k-3, k-2, k-1, k]
      (이때 정답(correct_pos)이 이 범위 밖이면, 블록을 정답이 포함되도록 한 칸씩 앞으로 당김)
    - k<5: 가능한 경계를 채우고, 부족하면 맨 뒤(k)에 붙임
    """
    if k <= 0:
        return [0, 0, 0, 0, 0]

    if k >= 5:
        start = k - 4  # 기본은 "항상 맨 뒤 5개"

        # ✅ 단, 정답이 블록 밖이면 정답이 들어오도록 블록을 앞으로 당김
        if correct_pos < start:
            start = correct_pos  # 정답이 블록의 마지막이 되게(= start..start+4)
            if start > k - 4:
                start = k - 4
            if start < 1:
                start = 1

        return list(range(start, start + 5))

    # k < 5
    boundaries = list(range(1, k + 1))
    pos = boundaries[:]
    while len(pos) < 5:
        pos.append(k)
    return pos[:5]

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아(문장 2개 이상 필요)."

    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)
    correct_pos = min(max(idx, 1), k)  # 1..k로 클램프

    mark_positions = choose_mark_positions(k, correct_pos)

    answer_index = mark_positions.index(correct_pos)  # 0..4
    answer_plain = ANS[answer_index]

    passage_with_marks = render_with_marks(remaining, mark_positions)

    return {
        "insert_sentence": insert_sent.strip(),
        "passage_with_marks": passage_with_marks,
        "answer_plain": answer_plain,
    }, None

# ---------------- 상태(✅ 예전 기능 복구) ----------------
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
    st.session_state["show_input"] = False     # ✅ 입력창 숨김
    st.session_state["passage_text"] = ""      # ✅ 입력 내용 즉시 삭제
    st.session_state["error_msg"] = ""

def on_show_answer():
    if st.session_state.get("prob") is not None:
        st.session_state["show_answer"] = True

def on_new_passage():
    st.session_state["prob"] = None
    st.session_state["show_answer"] = False
    st.session_state["show_input"] = True      # ✅ 입력창 다시 보이기
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
