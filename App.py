import re
import random
import streamlit as st

# ---------------- 배경 이미지 (방법 A: URL) ----------------
def set_background(image_url: str):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/KimJeongYun20167/Not-Exam4U-JoyforU/main/IMG_5661.jpeg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 글 가독성 확보: 본문 영역에 반투명 흰 박스 */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.86);
            padding: 2rem;
            border-radius: 18px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.set_page_config(page_title="이제 호그와트로!", layout="centered")

# ⚠️ 여기 BG_URL을 'raw.githubusercontent.com/.../IMG_5661.jpeg' 형태로 바꿔야 배경이 뜸
BG_URL = "https://raw.githubusercontent.com/KimJeongYun20167/Not-Exam4U-JoyforU/main/IMG_5661.jpeg"
set_background(BG_URL)

# ---------------- 출제 로직 ----------------
MARKS = ["①", "②", "③", "④", "⑤"]   # 지문 표식
ANS = ["1", "2", "3", "4", "5"]       # 정답은 숫자만

def split_sentences(text: str):
    """
    지문 텍스트 자체를 바꾸지 않고(의미/표현 수정 X),
    내부적으로만 문장 경계를 '판정'하기 위한 최소 분리기.
    """
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
    - 충분히 길면: 정답 포함 '연속 5개 경계' 블록
    - 짧으면: 존재하는 경계에 앞에서부터 ①~를 배치하고,
             남는 표식은 맨 뒤 경계(k)에 붙여서 5개를 맞춤
             (텍스트 변형 없이 표식 배치만 조정)
    """
    if k <= 0:
        return [0, 0, 0, 0, 0]

    # 경계 후보: 1..k (0=맨앞은 기본적으로 제외)
    boundaries = list(range(1, k + 1))

    if k >= 5:
        # 연속 블록 start: 1..k-4
        min_start = 1
        max_start = k - 4

        start_low = max(min_start, correct_pos - 4)
        start_high = min(max_start, correct_pos)

        if start_low <= start_high:
            start = random.randint(start_low, start_high)
        else:
            start = random.randint(min_start, max_start)

        return list(range(start, start + 5))

    # k < 5: 짧은 지문 대응 (⑤를 맨 뒤로 보내는 느낌)
    pos = boundaries[:]  # 길이 k
    while len(pos) < 5:
        pos.append(k)    # 맨 뒤 경계에 붙임
    return pos[:5]

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아(문장 2개 이상 필요)."

    idx = pick_random_sentence_index(sents)

    # 삽입 문장 1개 뽑고 제거
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)

    # 정답 경계(1..k로 클램프). idx가 0이면 맨 앞이지만, 기본적으로 1로 올려줌.
    correct_pos = min(max(idx, 1), k)

    mark_positions = choose_mark_positions(k, correct_pos)

    # 정답 번호: correct_pos가 mark_positions에서 처음 등장하는 위치(1~5)
    answer_index = mark_positions.index(correct_pos)  # 0..4
    answer_plain = ANS[answer_index]

    passage_with_marks = render_with_marks(remaining, mark_positions)

    return {
        "insert_sentence": insert_sent.strip(),
        "passage_with_marks": passage_with_marks,
        "answer_plain": answer_plain,
    }, None

# ---------------- 상태 ----------------
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
    st.session_state["show_input"] = False   # 입력 숨김(추론 방지)
    st.session_state["passage_text"] = ""    # 입력 비움
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
st.caption("너무 졸리다")

if st.session_state["error_msg"]:
    st.error(st.session_state["error_msg"])

if st.session_state["show_input"]:
    st.text_area("지문 입력", key="passage_text", height=220)

col1, col2, col3 = st.columns(3)
with col1:
    st.button("문제 생성", type="primary", on_click=on_generate)
with col2:
    st.button("정답 보기", on_click=on_show_answer)
with col3:
    st.button("새 지문", on_click=on_new_passage)

# 출력(시험지처럼: 불필요한 라벨 최소화)
if st.session_state["prob"] is not None:
    st.info(st.session_state["prob"]["insert_sentence"])
    st.write(st.session_state["prob"]["passage_with_marks"])

    if st.session_state["show_answer"]:
        st.success(st.session_state["prob"]["answer_plain"])
