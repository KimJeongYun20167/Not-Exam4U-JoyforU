import re
import random
import streamlit as st

st.set_page_config(page_title="문장삽입 문제 생성기", layout="centered")

def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if len(s.strip()) >= 2]

def pick_random_sentence_index(sentences):
    if len(sentences) >= 5:
        return random.randrange(1, len(sentences) - 1)
    return random.randrange(0, len(sentences))

def build_positions(n_remaining_sentences):
    return list(range(n_remaining_sentences + 1))

def render_text_with_slots(remaining, option_positions, option_labels):
    out = []
    for i in range(len(remaining) + 1):
        if i in option_positions:
            label = option_labels[option_positions.index(i)]
            out.append(f"({label})")
        if i < len(remaining):
            out.append(remaining[i])
    return " ".join(out)

def make_problem(passage_text, seed=None):
    if seed is not None:
        random.seed(seed)

    sents = split_sentences(passage_text)
    if len(sents) < 7:
        return None, "지문이 너무 짧아. 최소 7문장 이상이면 좋아."

    idx = pick_random_sentence_index(sents)
    insert_sent = sents[idx]
    remaining = sents[:idx] + sents[idx + 1:]
    correct_pos = idx

    positions = build_positions(len(remaining))
    if len(positions) < 5:
        return None, "지문이 너무 짧음"

    other_positions = [p for p in positions if p != correct_pos]
    random.shuffle(other_positions)

    picked = [correct_pos]
    for p in other_positions:
        if len(picked) == 5:
            break
        if all(abs(p - q) >= 2 for q in picked):
            picked.append(p)
    for p in other_positions:
        if len(picked) == 5:
            break
        if p not in picked:
            picked.append(p)

    option_positions = sorted(picked)
    labels = ["1", "2", "3", "4", "5"]
    passage_with_slots = render_text_with_slots(remaining, option_positions, labels)

    answer_index = option_positions.index(correct_pos)
    answer_label = labels[answer_index]

    return {
        "insert_sentence": insert_sent,
        "passage_with_slots": passage_with_slots,
        "answer": answer_label,
    }, None

st.title("🧩 문장 삽입 변형 문제 생성기")
st.caption("드레이코 말포이와 영어로 대화하자!")

passage = st.text_area("지문 입력", height=240, placeholder="지문 붙여넣기")
seed = st.number_input("랜덤 고정(seed, 선택)", min_value=0, value=0, step=1)

if st.button("문제 만들기", type="primary"):
    prob, err = make_problem(passage_text=passage, seed=seed if seed != 0 else None)

    if err:
        st.error(err)
    else:
        st.subheader("삽입할 문장")
        st.info(prob["insert_sentence"])

        st.subheader("문제 (1~5 중 가장 적절한 위치)")
        st.write(prob["passage_with_slots"])

        if st.button("정답 보기"):
            st.success(f"정답: {prob['answer']}")
