import streamlit as st
import json
from openai import OpenAI

client = OpenAI()

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="📚"
)

st.title("📚 AI Flashcard Generator")

topic = st.text_input(
    "Enter Topic",
    placeholder="Biology Chapter 1: Cells"
)

def generate_flashcards(topic):
    prompt = f"""
    Create 10 flashcards for the topic:

    {topic}

    Return only valid JSON.

    Format:

    [
      {{
        "question": "...",
        "answer": "..."
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

    return json.loads(content)

if "cards" not in st.session_state:
    st.session_state.cards = []

if "index" not in st.session_state:
    st.session_state.index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if st.button("Generate Flashcards"):

    if topic.strip():

        with st.spinner("Generating..."):
            try:
                cards = generate_flashcards(topic)

                st.session_state.cards = cards
                st.session_state.index = 0
                st.session_state.show_answer = False

            except Exception as e:
                st.error(str(e))

cards = st.session_state.cards

if cards:

    current = cards[st.session_state.index]

    st.subheader(
        f"Card {st.session_state.index + 1} / {len(cards)}"
    )

    st.markdown("### Question")
    st.info(current["question"])

    if st.button("Flip Card"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.markdown("### Answer")
        st.success(current["answer"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Previous"):
            if st.session_state.index > 0:
                st.session_state.index -= 1
                st.session_state.show_answer = False
                st.rerun()

    with col2:
        if st.button("Next"):
            if st.session_state.index < len(cards) - 1:
                st.session_state.index += 1
                st.session_state.show_answer = False
                st.rerun()
