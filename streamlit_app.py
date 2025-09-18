# app.py
import streamlit as st
import random
import pandas as pd
import io
from datetime import datetime
import json

st.set_page_config(page_title="Healthcare Quiz", page_icon="🩺", layout="centered")

# -----------------------------
# YOUR QUESTION BANK (unchanged)
# -----------------------------
QUESTIONS = [
    {
        "prompt": "Which of the following is considered Stage 2 Hypertension?",
        "options": ["130/80 mmHg", "140/90 mmHg", "150/95 mmHg", "160/100 mmHg"],
        "answer": "160/100 mmHg",
        "explanation": "Stage 2 hypertension is generally systolic ≥140 or diastolic ≥90 by AHA, but 160/100 is clearly Stage 2 in older criteria."
    },
    {
        "prompt": "First-line oral drug for Type 2 Diabetes is:",
        "options": ["Insulin", "Sulfonylureas", "Metformin", "Pioglitazone"],
        "answer": "Metformin",
        "explanation": "Metformin is the standard first-line therapy unless contraindicated."
    },
    {
        "prompt": "Which electrolyte imbalance is most likely with loop diuretics?",
        "options": ["Hyperkalemia", "Hypokalemia", "Hypernatremia", "Hypocalcemia"],
        "answer": "Hypokalemia",
        "explanation": "Loop diuretics increase potassium excretion, causing hypokalemia."
    },
    {
        "prompt": "Which hormone regulates blood calcium by increasing bone resorption?",
        "options": ["Calcitonin", "Parathyroid Hormone (PTH)", "Insulin", "Aldosterone"],
        "answer": "Parathyroid Hormone (PTH)",
        "explanation": "PTH increases bone resorption and calcium reabsorption in kidneys."
    },
    {
        "prompt": "Which class of drugs does Atenolol belong to?",
        "options": ["Calcium Channel Blocker", "Beta-blocker", "ACE Inhibitor", "Diuretic"],
        "answer": "Beta-blocker",
        "explanation": "Atenolol is a cardioselective beta-blocker used in hypertension and angina."
    },
    {
        "prompt": "HbA1c reflects average blood glucose over:",
        "options": ["1 week", "1 month", "3 months", "6 months"],
        "answer": "3 months",
        "explanation": "HbA1c reflects mean glucose over the lifespan of red blood cells (~120 days)."
    },
    {
        "prompt": "Which of the following is a Proton Pump Inhibitor (PPI)?",
        "options": ["Ranitidine", "Sucralfate", "Omeprazole", "Metoclopramide"],
        "answer": "Omeprazole",
        "explanation": "PPIs like omeprazole block gastric acid secretion."
    },
    {
        "prompt": "Which cranial nerve controls eye movement via the lateral rectus muscle?",
        "options": ["Oculomotor (III)", "Trochlear (IV)", "Abducens (VI)", "Optic (II)"],
        "answer": "Abducens (VI)",
        "explanation": "The abducens nerve controls the lateral rectus muscle (abduction of the eye)."
    },
    {
        "prompt": "Which of the following is NOT a symptom of Diabetes Mellitus?",
        "options": ["Polyuria", "Polydipsia", "Polyphagia", "Bradycardia"],
        "answer": "Bradycardia",
        "explanation": "Classic '3 Ps' are polyuria, polydipsia, and polyphagia."
    },
    {
        "prompt": "Which vitamin deficiency causes rickets in children?",
        "options": ["Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D"],
        "answer": "Vitamin D",
        "explanation": "Vitamin D deficiency impairs bone mineralization, leading to rickets."
    }
]

# -----------------------------
# Session-state initialization
# -----------------------------
if 'started' not in st.session_state:
    st.session_state.started = False
if 'quiz' not in st.session_state:
    st.session_state.quiz = []
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# -----------------------------
# Sidebar controls (start)
# -----------------------------
st.sidebar.title("Quiz settings")
num_questions = st.sidebar.slider("Number of questions", min_value=1, max_value=len(QUESTIONS), value=min(10, len(QUESTIONS)))
shuffle = st.sidebar.checkbox("Shuffle questions", value=True)

if not st.session_state.started:
    st.title("🎈 Healthcare Quiz")
    st.write("A simple multiple-choice quiz. Click **Start Quiz** when you're ready.")
    if st.button("Start Quiz"):
        # prepare quiz list
        if shuffle:
            st.session_state.quiz = random.sample(QUESTIONS, k=num_questions)
        else:
            st.session_state.quiz = QUESTIONS[:num_questions]
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.submitted = False
        st.session_state.started = True
        st.experimental_rerun()

# -----------------------------
# Quiz UI
# -----------------------------
if st.session_state.started:
    total_q = len(st.session_state.quiz)
    current = st.session_state.idx
    q = st.session_state.quiz[current]

    st.markdown(f"**Question {current+1} of {total_q}**")
    st.subheader(q['prompt'])

    choice_key = f"choice_{current}"
    # default selection handling (so it's visible when rerun)
    if choice_key not in st.session_state:
        st.session_state[choice_key] = None

    # show options
    selected = st.radio("Select one option:", q['options'], key=choice_key)

    # Submit button only if not yet submitted
    if not st.session_state.submitted:
        if st.button("Submit Answer"):
            if not selected:
                st.warning("Please select an option before submitting.")
            else:
                is_correct = (selected == q['answer'])
                if is_correct:
                    st.session_state.score += 1
                st.session_state.answers.append({
                    "Question": q['prompt'],
                    "Chosen": selected,
                    "Correct_answer": q['answer'],
                    "Correct": is_correct,
                    "Explanation": q.get('explanation', '')
                })
                st.session_state.submitted = True
                st.experimental_rerun()
    else:
        # Feedback + explanation
        last = st.session_state.answers[-1]
        if last["Correct"]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect — correct answer: **{last['Correct_answer']}**")
        st.info(last.get("Explanation", ""))
        # Next / Finish
        if current + 1 < total_q:
            if st.button("Next Question"):
                st.session_state.idx += 1
                st.session_state.submitted = False
                st.experimental_rerun()
        else:
            st.success("🎉 You've reached the end of the quiz.")
            st.write(f"**Final score: {st.session_state.score} / {total_q}**")

            # Show review table
            df = pd.DataFrame(st.session_state.answers)
            st.markdown("### Review answers")
            st.dataframe(df[["Question", "Chosen", "Correct_answer", "Correct"]])

            # Download results
            result_meta = {
                "timestamp": datetime.utcnow().isoformat(),
                "score": st.session_state.score,
                "total": total_q
            }
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            csv_bytes = csv_buf.getvalue().encode('utf-8')
            st.download_button("Download results (CSV)", data=csv_bytes, file_name="quiz_results.csv", mime="text/csv")

            # Restart
            if st.button("Restart quiz"):
                # reset state
                st.session_state.started = False
                st.session_state.quiz = []
                st.session_state.idx = 0
                st.session_state.score = 0
                st.session_state.answers = []
                st.session_state.submitted = False
                # clear choice keys
                for k in list(st.session_state.keys()):
                    if str(k).startswith("choice_"):
                        del st.session_state[k]
                st.experimental_rerun()
