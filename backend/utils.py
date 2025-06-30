import PyPDF2
import os
import google.generativeai as genai
from dotenv import load_dotenv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def parse_document(file):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    else:
        content = file.file.read().decode("utf-8")
    
    chunks = [content[i:i+1500] for i in range(0, len(content), 1500)]
    return content, chunks

def get_summary(content):
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    start = time.time()
    response = model.generate_content(f"Summarize the following document in less than 150 words:\n\n{content[:4000]}")
    print("Gemini summary time:", time.time() - start)
    return response.text.strip()

def answer_question(question, chunks, history):
    context = chunks[0]
    history_prompt = ""
    if history:
        for turn in history[-3:]:
            history_prompt += f"Q: {turn['q']}\nA: {turn['a']}\n"
    prompt = (
        f"{history_prompt}\n"
        f"Based on the following document, answer the question and justify with a reference (e.g., 'See paragraph 2'). "
        f"Also, provide the exact supporting snippet from the document.\n\n"
        f"Document:\n{context}\n\nQuestion: {question}"
    )
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    answer = response.text.strip()
    # Extract snippet (simple heuristic: return first quoted text or first 200 chars)
    import re
    snippet_match = re.search(r'"([^"]{20,})"', answer)
    snippet = snippet_match.group(1) if snippet_match else context[:200]
    justification = "See context above."
    return answer, justification, snippet

def generate_logic_questions(chunks):
    context = chunks[0]
    prompt = f"Generate three logic-based or comprehension-focused questions based on this document:\n\n{context}"
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    print("Gemini challenge response:", repr(response.text))
    questions = [q.strip("- ").strip() for q in response.text.strip().split("\n") if q.strip()]
    print("Parsed questions:", questions)
    return questions[:3]

def evaluate_answer(user_answers, questions, chunks):
    context = chunks[0]
    feedback = []
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    for i, ans in enumerate(user_answers):
        prompt = (
            f"Document: {context}\n"
            f"Question: {questions[i]}\n"
            f"User's answer: {ans}\n"
            f"Evaluate the answer, provide feedback, and justify with a reference and a supporting snippet."
        )
        response = model.generate_content(prompt)
        feedback.append(response.text.strip())
    return feedback

def generate_wordcloud(content, session_id):
    if not content.strip():
        raise ValueError("Document content is empty, cannot generate word cloud.")
    wc = WordCloud(width=800, height=400, background_color='white').generate(content)
    img_path = f"wordcloud_{session_id}.png"
    wc.to_file(img_path)
    print(f"Word cloud saved to: {img_path}")
    print(f"File exists: {os.path.exists(img_path)}")
    return img_path