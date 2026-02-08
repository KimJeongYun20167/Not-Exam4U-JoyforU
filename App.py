import re
import random
import streamlit as st

st.set_page_config(page_title="이제 호그와트로!", layout="centered")

MARKS = ["①", "②", "③", "④", "⑤"]   # 지문 표시
ANS = ["1", "2", "3", "4", "5"]       # 정답(숫자만)

def split_sentences(text: str):
    # 텍스트 변형 최소화: 문장 단위만 "판정" (표시는 원문 그대로 join)
    # - 문장 끝: . ? !
    # - 줄바꿈이 있어도 \s로 처리
    text_stripped = text.strip()
    if not text_stripped:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text_stripped)
    return [s for s in sents if len(s.strip()) >= 2]

def pick_random_sentence_index(sentences):
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def render_with_marks(remaining, positions_for_marks):
    """
    positions_for_marks: 길이 5 리스트.
    각 원소는 경계 인덱스 i (i는 0..len(remaining) 가능)
    - i=0: 맨 앞
    - i=len(remaining): 맨 뒤
    (우리는 기본적으로 0은 피하지만, 너무 짧으면 어쩔 수 없이 쓸 수 있게 열어둠)
    """
    # 같은 위치에 여러 표식이 있을 수 있으므로: 위치->표식 리스트로 모은다
    pos2labels = {}
    for j, pos in enumerate(positions_for_marks):
        pos2labels.setdefault(pos, []).append(MARKS[j])

    out = []
    for i in range(len(remaining) + 1):
        if i in pos2labels:
            # 같은 위치에 여러 개면 (④)(⑤)처럼 붙여서 출력
            out.append("".join([f"({lab})" for lab in pos2labels[i]]))
        if i < len(remaining):
            out.append(remaining[i])
    return " ".join(out)

def choose_mark_positions(k, correct_pos):
    """
    k = remaining 문장 수
    가능한 경계는 1..k (0=맨 앞은 보통 제외)
    목표: ①~⑤를 항상 순서대로 배치.
    - k>=5면: 최대한 '연속 5개' 블록을 쓰되 정답 포함
    - k<5면: 있는 경계에 앞에서부터 배치하고, 남는 건 맨 끝(k)에 붙임
    """
    if k <= 0:
        # 문장 1개도 없으면 어쩔 수 없음: 전부 맨 끝(0)
        return [0, 0, 0, 0, 0]

    boundaries = list(range(1, k + 1))  # 맨 앞(0) 제외

    # 1) 충분히 길면: 연속 5개 블록
    if k >= 5:
        # 가능한 시작: 1..k-4
        min_start = 1
        max_start = k - 4

        # 정답이 블록 안에 포함되도록 start 범위를 제한
        start_low = max(min_start, correct_pos - 4)
        start_high = min(max_start, correct_pos)

        if start_low <= start_high:
            start = random.randint(start_low, start_high)
        else:
            start = random.randint(min_start, max_start)

        return list(range(start, start + 5))  # 연속 5개

    # 2) k<5면: 있는 경계에 순서대로 배치 + 남는 표식은 맨 끝으로
    pos = boundaries[:]  # 길이 k
    while len(pos) < 5:
        pos.append(k)    # 맨 뒤 경계에 붙이기(⑤를 맨 뒤로 보내는 효과)
    return pos[:5]

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 2:
        return None, "지문이 너무 짧아(문장 2개 이상 필요)."

    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)               # 남은 문장 수
    correct_pos = min(max(idx, 1), k)  # 정답 경계(1..k로 클램프)

    mark_positions = choose_mark_positions(k, correct_pos)

    # 정답 번호: 정답 경계가 mark_positions에서 몇 번째인지(1~5)
    # 만약 k<5에서 정답 경계가 중복/끝붙임 때문에 여러 번 있을 수 있으니 "첫 등장"을 정답으로
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
    st.session_state["show_input"] = False      # 입력 숨김(추론 방지)
    st.session_state["passage_text"] = ""       # 입력 비움
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

if st.session_state["prob"] is not None:
    st.info(st.session_state["prob"]["insert_sentence"])
    st.write(st.session_state["prob"]["passage_with_marks"])
    if st.session_state["show_answer"]:
        st.success(st.session_state["prob"]["answer_plain"])
