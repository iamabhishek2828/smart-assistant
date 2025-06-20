import streamlit as st
import requests
import time
import io

st.set_page_config(page_title="Smart Research Assistant", layout="wide", page_icon="🧠")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("🧠 Smart Assistant")
    st.markdown("""
    **Features:**
    - 📄 PDF/TXT Upload & Summarization
    - 🤖 Ask Anything (QA)
    - 🧩 Challenge Me (Logic Qs)
    - 📝 Conversation Memory
    - ✨ Highlighted Justifications
    - ⬇️ Downloadable Summary

    ---
    **Instructions:**
    1. Upload a document.
    2. Explore the tabs: Ask Anything or Challenge Me.
    3. Enjoy interactive, AI-powered research help!
    """)
    st.markdown("---")
    st.caption("Made by Abhishek Choudhary • 2025")

st.title("🧠 Smart Assistant for Research Summarization")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("📤 Upload PDF or TXT", type=["pdf", "txt"])
if uploaded_file:
    st.info(f"**Uploaded:** `{uploaded_file.name}` ({uploaded_file.size/1024:.1f} KB)")
    with st.spinner("Analyzing document and generating summary..."):
        res = requests.post("http://localhost:8000/upload", files={"file": uploaded_file})
        data = res.json()
        time.sleep(0.5)
    if "error" in data:
        st.error(f"Backend error: {data['error']}")
    else:
        st.session_state.session_id = data["session_id"]
        st.session_state.history = []
        st.session_state["summary"] = data["summary"]  # <--- cache summary!
        st.success("✅ Document uploaded and summarized!")
        st.write("### 📑 Document Summary")
        st.info(data["summary"])

if st.session_state.session_id:
    tabs = st.tabs(["🤖 Ask Anything", "🧩 Challenge Me", "🕑 Conversation History", "⬇️ Download"])
    # --- Ask Anything Tab ---
    with tabs[0]:
        st.subheader("Ask Anything")
        question = st.text_input("Type your question about the document:")
        if st.button("Ask", key="ask_btn"):
            with st.spinner("Thinking..."):
                res = requests.post("http://localhost:8000/ask", json={
                    "session_id": st.session_state.session_id,
                    "question": question
                })
                data = res.json()
                time.sleep(0.5)
            st.session_state.history.append({"q": question, "a": data["answer"], "snippet": data["snippet"]})
            st.success("**Answer:**")
            st.write(data["answer"])
            st.info(f"**Justification:** {data['justification']}")
            st.markdown(
                f"<span style='background-color: #ffe066; color: #222; padding: 2px 4px; border-radius: 4px'>{data['snippet']}</span>",
                unsafe_allow_html=True
            )

            if st.button("👍 Helpful", key=f"helpful_{len(st.session_state.history)}"):
                st.success("Thanks for your feedback!")
            if st.button("👎 Not Helpful", key=f"not_helpful_{len(st.session_state.history)}"):
                st.warning("Feedback noted. We'll improve!")

        with st.expander("🔍 Ask about a specific passage"):
            selected_text = st.text_area("Paste or type a passage from the document:")
            followup_q = st.text_input("Your question about this passage:")
            if st.button("Ask about Passage"):
                res = requests.post("http://localhost:8000/ask", json={
                    "session_id": st.session_state.session_id,
                    "question": f"{followup_q}\n\n[Context passage: {selected_text}]"
                })
                data = res.json()
                st.write("**Answer:**", data["answer"])
                st.info(f"**Justification:** {data['justification']}")
                st.markdown(
                    f"<span style='background-color: #e0f7fa; color: #222; padding: 2px 4px; border-radius: 4px'>{data['snippet']}</span>",
                    unsafe_allow_html=True
                )

    # --- Challenge Me Tab ---
    with tabs[1]:
        st.subheader("Challenge Me")
        if "challenge_qs" not in st.session_state:
            if st.button("Start Challenge"):
                with st.spinner("Generating challenge questions..."):
                    res = requests.post("http://localhost:8000/challenge", json={
                        "session_id": st.session_state.session_id,
                        "question": ""
                    })
                    st.session_state.challenge_qs = res.json()["questions"]
                    st.session_state.challenge_answers = [""] * 3
        if "challenge_qs" in st.session_state:
            st.write("#### Answer these questions:")
            for i, q in enumerate(st.session_state.challenge_qs):
                st.session_state.challenge_answers[i] = st.text_input(f"Q{i+1}: {q}", value=st.session_state.challenge_answers[i], key=f"challenge_{i}")
            if st.button("Submit Answers"):
                with st.spinner("Evaluating your answers..."):
                    res = requests.post("http://localhost:8000/evaluate", json={
                        "session_id": st.session_state.session_id,
                        "user_answers": st.session_state.challenge_answers
                    })
                    feedback = res.json()["feedback"]
                    for i, fb in enumerate(feedback):
                        st.info(f"**Feedback for Q{i+1}:** {fb}")
            if st.button("Reset Challenge"):
                del st.session_state.challenge_qs
                del st.session_state.challenge_answers

    # --- Conversation History Tab ---
    with tabs[2]:
        st.subheader("Conversation History")
        if st.session_state.history:
            for turn in st.session_state.history[::-1]:
                st.markdown(f"**Q:** {turn['q']}")
                st.markdown(f"**A:** {turn['a']}")
                st.markdown(f"<span style='background-color: #e0f7fa; color: #222; padding: 2px 4px; border-radius: 4px'>{turn['snippet']}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No conversation yet. Start by asking a question!")

    # --- Download Tab ---
    with tabs[3]:
        st.subheader("Download Full Session as PDF")
        if st.session_state.session_id:
            if st.button("Download PDF Report"):
                res = requests.post("http://localhost:8000/export_pdf", json={"session_id": st.session_state.session_id})
                with open("session_report.pdf", "wb") as f:
                    f.write(res.content)
                with open("session_report.pdf", "rb") as f:
                    st.download_button("Download PDF", f, file_name="session_report.pdf")

    if st.session_state.session_id:
        if st.button("Show Word Cloud"):
            res = requests.post(
                "http://localhost:8000/wordcloud",
                json={"session_id": st.session_state.session_id, "question": ""}
            )
            if res.status_code == 200:
                st.image(io.BytesIO(res.content), caption="Document Word Cloud")
            else:
                try:
                    error_msg = res.json().get("error", "Unknown error")
                except Exception:
                    error_msg = "Unknown error"
                st.error(f"Failed to generate word cloud: {error_msg}")