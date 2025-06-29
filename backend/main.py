from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from utils import parse_document, get_summary, answer_question, generate_logic_questions, evaluate_answer, generate_wordcloud
from fpdf import FPDF
import uuid

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sessions = {}

class QARequest(BaseModel):
    session_id: str
    question: str

class ChallengeRequest(BaseModel):
    session_id: str
    user_answers: list

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        content, chunks = parse_document(file)
        session_id = str(uuid.uuid4())  # Use a unique session ID
        sessions[session_id] = {"content": content, "chunks": chunks, "history": [], "challenge_qs": []}
        summary = get_summary(content)
        return {"session_id": session_id, "summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask")
async def ask(req: QARequest):
    doc = sessions[req.session_id]
    answer, justification, snippet = answer_question(req.question, doc["chunks"], doc["history"])
    doc["history"].append({"q": req.question, "a": answer, "snippet": snippet})
    return {"answer": answer, "justification": justification, "snippet": snippet}

@app.post("/challenge")
async def challenge(req: QARequest):
    doc = sessions[req.session_id]
    questions = generate_logic_questions(doc["chunks"])
    doc["challenge_qs"] = questions
    return {"questions": questions}

@app.post("/evaluate")
async def evaluate(req: ChallengeRequest):
    try:
        doc = sessions[req.session_id]
        if not doc.get("challenge_qs"):
            raise ValueError("No challenge questions found for this session. Please start a challenge first.")
        feedback = evaluate_answer(req.user_answers, doc["challenge_qs"], doc["chunks"])
        return {"feedback": feedback}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/export_pdf")
async def export_pdf(req: QARequest):
    doc = sessions[req.session_id]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Smart Assistant Session Report", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Summary:\n{doc.get('summary', '')}\n")
    pdf.ln(5)
    pdf.cell(0, 10, "Conversation History:", ln=True)
    for turn in doc.get("history", []):
        pdf.multi_cell(0, 10, f"Q: {turn['q']}\nA: {turn['a']}\nSnippet: {turn['snippet']}\n")
        pdf.ln(2)
    pdf_file = f"session_{req.session_id}.pdf"
    pdf.output(pdf_file)
    return FileResponse(pdf_file, filename="session_report.pdf", media_type="application/pdf")

@app.post("/wordcloud")
async def wordcloud(req: QARequest):
    try:
        doc = sessions[req.session_id]
        img_path = generate_wordcloud(doc["content"], req.session_id)
        print(f"Returning image file: {img_path}")
        return FileResponse(img_path, media_type="image/png")
    except Exception as e:
        print(f"Wordcloud generation error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def read_root():
    return {"message": "Smart Assistant backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)