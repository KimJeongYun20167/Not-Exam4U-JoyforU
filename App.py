import re
import random
import streamlit as st

st.set_page_config(page_title="문장삽입 문제 생성기", layout="centered")

# 표시 라벨(원하면 ①②③④⑤ 대신 1~5로 바꿔도 됨)
MARKS = ["①", "②", "③", "④", "⑤"]   # 지문에 찍히는 표식
ANS = ["1", "2", "3", "4", "5"]       # 정답은 숫자만 출력(요구사항)

def split_sentences(text: str):
    # MVP 문장 분리: . ? ! 뒤 공백 기준
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text)
    sents = [s.strip() for s in sents if len(s.strip()) >= 2]
    return sents

def pick_random_sentence_index(sentences):
    # 첫/끝은 피해서 랜덤 (시험 문제 느낌)
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def render_with_consecutive_marks(remaining, start_pos):
    """
    start_pos부터 5개의 연속 경계에 (①)~(⑤) 찍기.
    경계 i는 remaining[i-1] 다음 위치 (i=1..len(remaining))
    """
    option_positions = list(range(start_pos, start_pos + 5))  # 연속 5개

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
        return None, "지문이 너무 짧아. 최소 7문장 이상이면 좋아."

    # 1) 삽입 문장 랜덤 선택 후 제거
    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    k = len(remaining)  # 남은 문장 수
    # 경계(삽입 위치)는 1..k (0=맨앞은 제외)
    correct_pos = idx
    if correct_pos == 0:
        # 혹시 첫 문장이 뽑히면(낮은 확률) 다시 뽑기
        idx = random.randrange(1, len(sents) - 1)
        insert_sent = sents[idx]
        remaining = sents[:idx] + sents[idx + 1:]
        k = len(remaining)
        correct_pos = idx

    # 2) (①~⑤)가 "연속"으로 찍히도록: 연속 5개 경계 블록 선택
    # 가능한 start 범위: 1..(k-4)
    if k < 6:
        return None, "문장이 너무 적어서 (①~⑤) 연속 표식을 만들기 어려워. 지문을 더 길게 해줘."

    min_start = 1
    max_start = k - 4

    # 정답 위치(correct_pos)가 반드시 블록 안에 들어가야 하므로
    # start는 [correct_pos-4, correct_pos] 범위를 우선으로 잡는다.
    start_low = max(min_start, correct_pos - 4)
    start_high = min(max_start, correct_pos)

    if start_low > start_high:
        # 이론상 거의 안 나오지만 안전장치
        start_pos = random.randint(min_start, max_start)
    else:
        start_pos = random.randint(start_low, start_high)

    passage_with_marks, option_positions = render_with_consecutive_marks(remaining, start_pos)

    # 정답은 블록 내에서 몇 번째인지(1~5)
    answer_index = correct_pos - start_pos  # 0..4
    answer_plain = ANS[answer_index]        # "1".."5"

    return {
        "insert_sentence": insert_sent,
        "passage_with_marks": passage_with_marks,
        "answer_plain": answer_plain,
    }, None


# ---------------- UI ----------------
st.title("🪄 이제 호그와트로!")

# 입력 UI를 문제 생성 후 숨기기 위한 상태
if "prob" not in st.session_state:
    st.session_state.prob = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "show_input" not in st.session_state:
    st.session_state.show_input = True

# 입력창: key를 줘야 생성 후 값을 지울 수 있음
if st.session_state.show_input:
    passage = st.text_area(
        "지문 입력",
        key="passage_text",
        height=220,
        placeholder="지문을 붙여 넣어줘!"
    )
else:
    passage = st.session_state.get("passage_text", "")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("문제 생성", type="primary"):
        prob, err = make_problem(passage)
        if err:
            st.session_state.prob = None
            st.session_state.show_answer = False
            st.error(err)
        else:
            st.session_state.prob = prob
            st.session_state.show_answer = False

            # ✅ 입력 지문을 화면에서 안 보이게 처리 (추론 방지)
            st.session_state.passage_text = ""   # 입력칸 비우기
            st.session_state.show_input = False  # 입력칸 숨기기

with col2:
    if st.button("정답 보기"):
        if st.session_state.prob is None:
            st.warning("먼저 ‘문제 생성’을 눌러줘.")
        else:
            st.session_state.show_answer = True

with col3:
    if st.button("새 지문"):
        # 다시 입력받기
        st.session_state.prob = None
        st.session_state.show_answer = False
        st.session_state.show_input = True
        st.session_state.passage_text = ""

# 출력 (시험지처럼: 제목 텍스트 최소화)
if st.session_state.prob is not None:
    st.info(st.session_state.prob["insert_sentence"])
    st.write(st.session_state.prob["passage_with_marks"])

    if st.session_state.show_answer:
        st.success(st.session_state.prob["answer_plain"])
