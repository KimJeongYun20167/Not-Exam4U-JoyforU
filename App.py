import re
import random
import streamlit as st

st.set_page_config(page_title="문장삽입 문제 생성기", layout="centered")

# 보기 표시(시험 스타일)
CIRCLED = ["①", "②", "③", "④", "⑤"]
# 정답 출력(요구: 숫자만)
PLAIN = ["1", "2", "3", "4", "5"]

def split_sentences(text: str):
    """
    MVP용 문장 분리:
    . ? ! 뒤 공백 기준으로 자름.
    """
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if len(s.strip()) >= 2]

def pick_random_sentence_index(sentences):
    """
    가능하면 첫/끝 문장을 피해서 랜덤 선택(문제 느낌 ↑).
    """
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def build_positions(n_remaining_sentences):
    """
    시험 형식 반영:
    지문 맨 앞(0)은 보기에 잘 안 내므로 제외.
    경계는 1..k (k = remaining 문장 수)
    """
    return list(range(1, n_remaining_sentences + 1))

def render_text_with_slots(remaining, option_positions):
    """
    option_positions의 값 i는 'remaining[i-1] 다음 위치'에 삽입 자리 표기.
    """
    out = []
    for i in range(len(remaining) + 1):
        if i in option_positions:
            label = CIRCLED[option_positions.index(i)]
            out.append(f"({label})")
        if i < len(remaining):
            out.append(remaining[i])
    return " ".join(out)

def make_problem(passage_text: str):
    sents = split_sentences(passage_text)
    if len(sents) < 7:
        return None, "지문이 너무 짧아. 최소 7문장 이상이면 좋아."

    # 1) 삽입 문장 랜덤 선택 후 제거
    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]

    # 제거 전 idx였던 위치 = 제거 후 삽입 경계 idx
    correct_pos = idx

    # 혹시라도 첫 문장이 뽑혀서(확률은 낮지만) 맨 앞이 정답이 되면 재샘플
    if correct_pos == 0:
        idx = random.randrange(1, len(sents) - 1)
        insert_sent = sents[idx]
        remaining = sents[:idx] + sents[idx + 1:]
        correct_pos = idx

    # 2) 보기 위치 후보 만들기(맨 앞 제외)
    positions = build_positions(len(remaining))
    if len(positions) < 5:
        return None, "삽입 위치 후보가 5개 미만이야. 지문을 더 길게 해줘."

    # 정답 포함 + 나머지 4개 랜덤
    other_positions = [p for p in positions if p != correct_pos]
    random.shuffle(other_positions)

    picked = [correct_pos]
    # 너무 한 곳에 몰리지 않게 간단 분산
    for p in other_positions:
        if len(picked) == 5:
            break
        if all(abs(p - q) >= 2 for q in picked):
            picked.append(p)
    # 부족하면 채움
    for p in other_positions:
        if len(picked) == 5:
            break
        if p not in picked:
            picked.append(p)

    option_positions = sorted(picked)

    # 정답 번호(1~5): option_positions에서 정답이 몇 번째인지
    answer_index = option_positions.index(correct_pos)  # 0..4
    answer_plain = PLAIN[answer_index]                  # "1".."5"

    passage_with_slots = render_text_with_slots(remaining, option_positions)

    return {
        "insert_sentence": insert_sent,
        "passage_with_slots": passage_with_slots,
        "answer_plain": answer_plain,
    }, None


# ---------------- UI ----------------
st.title("🧩 문장 삽입 변형 문제 생성기")
st.caption("말포이 존잘")

passage = st.text_area("지문 입력", height=260, placeholder="붙여넣기")

# session_state 초기화(버튼 rerun 문제 해결)
if "prob" not in st.session_state:
    st.session_state.prob = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

col1, col2 = st.columns(2)
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

with col2:
    if st.button("정답 보기"):
        if st.session_state.prob is None:
            st.warning("먼저 ‘문제 만들기’를 눌러서 문제를 생성해줘.")
        else:
            st.session_state.show_answer = True

# 출력
if st.session_state.prob is not None:
    st.subheader("삽입할 문장")
    st.info(st.session_state.prob["insert_sentence"])

    st.subheader("지문 (①~⑤ 중 가장 적절한 위치)")
    st.write(st.session_state.prob["passage_with_slots"])

    if st.session_state.show_answer:
        st.success(f"정답: {st.session_state.prob['answer_plain']}")
