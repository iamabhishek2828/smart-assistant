# 🧠 Smart Assistant for Research Summarization

A GenAI-powered assistant that reads, summarizes, and reasons over your research papers, legal documents, or technical manuals. Built with FastAPI, Streamlit, and Gemini (Google AI), this tool goes beyond basic summarization to deliver deep comprehension, logic-based challenges, and interactive research support.

---

## 🚀 Features

- **PDF/TXT Upload:** Instantly analyze structured English documents.
- **Auto Summary:** Get a concise summary (≤150 words) right after upload.
- **Ask Anything:** Free-form Q&A grounded in your document, with highlighted supporting snippets and justifications.
- **Challenge Me:** The AI generates logic/comprehension questions, evaluates your answers, and provides feedback with references.
- **Memory:** Maintains conversation history for context-aware follow-ups.
- **Answer Highlighting:** See the exact document snippet supporting each answer.
- **Downloadable Summary & Full Session PDF:** Export your summary or the entire session (Q&A, challenges, feedback) as TXT or PDF.
- **Document Word Cloud:** Visualize document keywords and topics.
- **Table of Contents:** Instantly generate and view a clickable outline of your document.
- **User Feedback:** Rate answers to help improve the assistant.

---

## 🖥️ Demo

https://smart-assistant-abhi22.streamlit.app/

---

## 🏗️ Architecture

- **Frontend:** Streamlit (Python) for a modern, interactive web UI.
- **Backend:** FastAPI (Python) for document parsing, LLM integration, and session management.
- **LLM:** Gemini (Google AI) for summarization, Q&A, and logic-based reasoning.
- **Session Memory:** Context-aware Q&A and challenge evaluation.
- **Visualization:** WordCloud and Matplotlib for document insights.

![architecture diagram](https://i.imgur.com/6pQw5kV.png) <!-- Replace with your own diagram if available -->

---

## ⚡ Quickstart

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/smart-assistant.git
cd smart-assistant
