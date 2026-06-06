import streamlit as st
import json
from openai import OpenAI

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Recallify",
    page_icon="📚",
    layout="centered"
)

# ---------------------------------
# API KEY CHECK
# ---------------------------------

if "OPENAI_API_KEY" not in st.secrets:
    st.error(
        "OPENAI_API_KEY not found in Streamlit Secrets."
    )
    st.stop()

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ---------------------------------
# SESSION STATE
# ---------------------------------

if "cards" not in st.session_state:
    st.session_state.cards = []

if "index" not in st.session_state:
    st.session_state.index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# ---------------------------------
# FLASHCARD GENERATOR
# ---------------------------------

def generate_flashcards(
    grade,
    board,
    subject,
    topic,
    count
):

    prompt = f"""
Create {count} flashcards.

Class: {grade}
Board: {board}
Subject: {subject}
Topic: {topic}

Rules:
1. Difficulty should match class level.
2. Questions should test active recall.
3. Answers should be short.
4. Return ONLY JSON.
5. No markdown.
6. No explanation.

Example:

[
  {{
    "question":"What is a cell?",
    "answer":"Basic unit of life"
  }}
]
"""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    content = content.replace(
        "```json", ""
    ).replace(
        "```", ""
    ).strip()

    return json.loads(content)

# ---------------------------------
# HEADER
# ---------------------------------

st.title("📚 Recallify")
st.caption(
    "Generate AI-powered flashcards instantly."
)

st.divider()

# ---------------------------------
# FORM
# ---------------------------------

with st.form("flashcard_form"):

    grade = st.selectbox(
        "Class",
        [
            "6","7","8","9",
            "10","11","12",
            "College"
        ]
    )

    board = st.selectbox(
        "Board",
        [
            "CBSE",
            "ICSE",
            "State Board",
            "NEET",
            "JEE",
            "General"
        ]
    )

    subject = st.selectbox(
        "Subject",
        [
            "Biology",
            "Physics",
            "Chemistry",
            "Mathematics",
            "History",
            "Geography",
            "English",
            "Computer Science"
        ]
    )

    topic = st.text_input(
        "Topic / Chapter",
        placeholder="Cell Structure and Function"
    )

    count = st.slider(
        "Number of Flashcards",
        5,
        30,
        10
    )

    submitted = st.form_submit_button(
        "🚀 Generate Flashcards"
    )

# ---------------------------------
# GENERATE
# ---------------------------------

if submitted:

    if topic.strip() == "":
        st.warning(
            "Please enter a topic."
        )

    else:

        with st.spinner(
            "Generating flashcards..."
        ):

            try:

                cards = generate_flashcards(
                    grade,
                    board,
                    subject,
                    topic,
                    count
                )

                if len(cards) == 0:
                    st.error(
                        "No flashcards generated."
                    )

                else:

                    st.session_state.cards = cards
                    st.session_state.index = 0
                    st.session_state.show_answer = False

                    st.success(
                        f"{len(cards)} flashcards generated."
                    )

            except Exception as e:
                st.error(str(e))

# ---------------------------------
# SHOW CARDS
# ---------------------------------

cards = st.session_state.cards

if len(cards) > 0:

    current = cards[
        st.session_state.index
    ]

    progress = (
        st.session_state.index + 1
    ) / len(cards)

    st.progress(progress)

    st.write(
        f"Card {st.session_state.index + 1} of {len(cards)}"
    )

    card_text = (
        current["answer"]
        if st.session_state.show_answer
        else current["question"]
    )

    card_title = (
        "Answer"
        if st.session_state.show_answer
        else "Question"
    )

    st.markdown(
        f"""
        <div style="
            border:2px solid #dcdcdc;
            border-radius:20px;
            padding:40px;
            min-height:250px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            text-align:center;
            font-size:28px;
            font-weight:600;
            margin-top:20px;
            margin-bottom:20px;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
        ">
            <div style="
                font-size:16px;
                color:gray;
                margin-bottom:20px;
            ">
                {card_title}
            </div>

            {card_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 Flip Card",
        key="flip"
    ):
        st.session_state.show_answer = (
            not st.session_state.show_answer
        )
        st.rerun()

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⬅ Previous",
            key="prev"
        ):

            if st.session_state.index > 0:

                st.session_state.index -= 1
                st.session_state.show_answer = False
                st.rerun()

    with col2:

        if st.button(
            "Next ➡",
            key="next"
        ):

            if st.session_state.index < len(cards)-1:

                st.session_state.index += 1
                st.session_state.show_answer = False
                st.rerun()

# ---------------------------------
# FOOTER
# ---------------------------------

st.divider()

st.caption(
    "Built with Streamlit + OpenAI"
)
