# streamlit_app.py
import streamlit as st
import asyncio
from project import run_startup_eval

st.set_page_config(
    page_title="Startup Idea Evaluator",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 Startup Idea Evaluator")
st.write(
    "Enter your startup idea, and our multi-agent system will analyze it "
    "from Market, Financial, and Tech perspectives."
)

# User input
startup_idea = st.text_area(
    "Describe your startup idea:",
    placeholder="E.g., An AI-powered platform for personalized learning..."
)

run_button = st.button("Evaluate Idea")

if run_button:
    if not startup_idea.strip():
        st.warning("Please enter a startup idea before running the evaluation.")
    else:
        # Clear previous results
        output_area = st.empty()
        progress_text = st.empty()
        st.info("Evaluating your idea. This may take a few seconds...")

        async def run_evaluator():
            result_text = ""
            line_count = 0
            async for line in run_startup_eval(startup_idea):
                line_count += 1
                result_text += line + "\n\n"
                output_area.text(result_text)
                progress_text.text(f"Processing... ({line_count} updates received)")
            
            progress_text.text("✅ Evaluation complete!")

        # Run the async function
        asyncio.run(run_evaluator())
