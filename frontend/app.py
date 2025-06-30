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

BACKEND_URL = "https://smart-assistant-backend-rf74.onrender.com"

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("📤 Upload PDF or TXT", type=["pdf", "txt"])
if uploaded_file:
    st.info(f"**Uploaded:** `{uploaded_file.name}` ({uploaded_file.size/1024:.1f} KB)")
    with st.spinner("Analyzing document and generating summary..."):
        res = requests.post(f"{BACKEND_URL}/upload", files={"file": uploaded_file})
        try:
            data = res.json()
        except Exception:
            st.error("Backend did not return valid JSON. Please check backend logs.")
            st.stop()
        time.sleep(0.5)
    if "error" in data:
        st.error(f"Backend error: {data['error']}")
    else:
        st.session_state.session_id = data["session_id"]
        st.session_state.history = []
        st.session_state["summary"] = data["summary"]
        # Reset challenge state on new upload
        if "challenge_qs" in st.session_state:
            del st.session_state["challenge_qs"]
        if "challenge_answers" in st.session_state:
            del st.session_state["challenge_answers"]
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
                res = requests.post(f"{BACKEND_URL}/ask", json={
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
                res = requests.post(f"{BACKEND_URL}/ask", json={
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
                    res = requests.post(f"{BACKEND_URL}/challenge", json={
                        "session_id": st.session_state.session_id,
                        "question": ""
                    })
                    questions = res.json().get("questions", [])
                    if questions:
                        st.session_state.challenge_qs = questions
                        st.session_state.challenge_answers = [""] * len(questions)
                    else:
                        st.error("Failed to generate challenge questions. Try again.")
            st.info("Click 'Start Challenge' to generate questions before submitting answers.")
        else:
            st.write("#### Answer these questions:")
            for i, q in enumerate(st.session_state.challenge_qs):
                st.session_state.challenge_answers[i] = st.text_input(
                    f"Q{i+1}: {q}",
                    value=st.session_state.challenge_answers[i],
                    key=f"challenge_{i}"
                )
            submit_disabled = any(ans.strip() == "" for ans in st.session_state.challenge_answers)
            if st.button("Submit Answers", disabled=submit_disabled):
                with st.spinner("Evaluating your answers..."):
                    res = requests.post(f"{BACKEND_URL}/evaluate", json={
                        "session_id": st.session_state.session_id,
                        "user_answers": st.session_state.challenge_answers
                    })
                    try:
                        data = res.json()
                    except Exception:
                        st.error("Backend did not return valid JSON. Please try again.")
                        st.stop()
                    if "error" in data:
                        st.error(f"Backend error: {data['error']}")
                    else:
                        feedback = data["feedback"]
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
                res = requests.post(f"{BACKEND_URL}/export_pdf", json={"session_id": st.session_state.session_id})
                with open("session_report.pdf", "wb") as f:
                    f.write(res.content)
                with open("session_report.pdf", "rb") as f:
                    st.download_button("Download PDF", f, file_name="session_report.pdf")

    if st.session_state.session_id:
        if st.button("Show Word Cloud"):
            res = requests.post(
                f"{BACKEND_URL}/wordcloud",
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