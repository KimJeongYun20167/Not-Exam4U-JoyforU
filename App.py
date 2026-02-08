import re
import random
import streamlit as st

st.set_page_config(page_title="이제 호그와트로!", layout="centered")

MARKS = ["①", "②", "③", "④", "⑤"]   # 지문 표시
ANS = ["1", "2", "3", "4", "5"]       # 정답 출력(숫자만)

def split_sentences(text: str):
    # MVP 문장 분리: . ? ! 뒤 공백 기준
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if len(s.strip()) >= 2]

def pick_random_sentence_index(sentences):
    # 가능하면 첫/끝 문장 피해서 랜덤
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def render_with_consecutive_marks(remaining, start_pos):
    # start_pos부터 연속 5개 경계에 ①~⑤를 찍음
    option_positions = list(range(start_pos, start_pos + 5))
    out = []
    for i in range(len(remaining) + 1):
        if i in option_positions:
            out.append(f"({MARKS[option_positions.index(i)]})")
        if i < len(remaining):
            out.append(remaining[i])
    return " ".join(out), option_positions

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 7:
       zyg
        return None, "지문이 너무 짧아. 최소 7문장 이상이면 좋아."

    # 삽입 문장 랜덤 선택 후 제거
    idx = pick_random_sentence_index(sents)

    # 첫 문장 뽑히면(정답 위치가 맨 앞이 됨) 다시 뽑기
    if idx == 0 and len(sents) > 2:
        idx = random.randrange(1, len(sents) - 1)

    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)  # 남은 문장 수
    # 경계는 1..k (0=맨 앞 위치는 제외)
    correct_pos = idx

    # 연속 5개 표식 블록 생성 가능 조건: k >= 6 (경계가 1..k이고, 그 중 5개 연속 필요)
    if k < 6:
        return None, "문장이 너무 적어서 (①~⑤) 연속 표식을 만들기 어려워. 지문을 더 길게 해줘."

    min_start = 1
    max_start = k - 4

    # 정답이 반드시 블록 안에 들어가게 start 범위 제한
    start_low = max(min_start, correct_pos - 4)
    start_high = min(max_start, correct_pos)

    start_pos = random.randint(start_low, start_high)

    passage_with_marks, option_positions = render_with_consecutive_marks(remaining, start_pos)

    # 정답 번호(1~5): 블록 안에서 몇 번째인지
    answer_index = correct_pos - start_pos  # 0..4
    answer_plain = ANS[answer_index]

    return {
        "insert_sentence": insert_sent,
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


# ---------------- 콜백(에러 방지 핵심) ----------------
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
    st.session_state["show_input"] = False      # 입력창 숨김(추론 방지)
    st.session_state["passage_text"] = ""       # 입력값 비움
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

if st.session_state.get("error_msg"):
    st.error(st.session_state["error_msg"])

if st.session_state["show_input"]:
    st.text_area("지문 입력", key="passage_text", height=220, placeholder="여기에 영어 지문을 붙여 넣어줘.")

col1, col2, col3 = st.columns(3)
with col1:
    st.button("문제 생성", type="primary", on_click=on_generate)
with col2:
    st.button("정답 보기", on_click=on_show_answer)
with col3:
    st.button("새 지문", on_click=on_new_passage)

# 출력(시험지처럼 문구 최소화)
if st.session_state["prob"] is not None:
    st.info(st.session_state["prob"]["insert_sentence"])
    st.write(st.session_state["prob"]["passage_with_marks"])

    if st.session_state["show_answer"]:
        st.success(st.session_state["prob"]["answer_plain"])
