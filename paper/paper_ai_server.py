import os
import re
import json
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from transformers import MT5ForConditionalGeneration, MT5Tokenizer, pipeline
import PyPDF2

MODEL_NAME = "google/mt5-base"
CHUNK_SIZE = 4000
MAX_CHUNKS = 10
DRAFTS_DIR = "./drafts"
os.makedirs(DRAFTS_DIR, exist_ok=True)

tokenizer = MT5Tokenizer.from_pretrained(MODEL_NAME)
model = MT5ForConditionalGeneration.from_pretrained(MODEL_NAME)
generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

app = FastAPI(title="Scientific Paper AI", version="1.0")
FILE_STORAGE = {}  # id -> text

def clean_text(text: str) -> str:
    text = re.sub(r"[^ء-يa-zA-Z0-9\s.,؛:؟\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def chunk_text(text: str):
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    if len(chunks) > MAX_CHUNKS:
        chunks = chunks[:MAX_CHUNKS]
        chunks.append("[Note: Text truncated due to file size]")
    return chunks

def extract_text_from_pdf(file) -> str:
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return clean_text(text)

def generate_text(prompt: str, max_new_tokens=500):
    outputs = generator(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7
    )
    return outputs[0]["generated_text"]

async def stream_generate(prompt: str, max_new_tokens=400):
    full_text = generate_text(prompt, max_new_tokens=max_new_tokens)
    chunks = chunk_text(full_text)
    for c in chunks:
        yield json.dumps({"chunk": c}) + "\n"
        await asyncio.sleep(0.01)

def prepare_prompt(
    type: str,
    text: str,
    language: str,
    question: Optional[str] = None,
    document_spec: Optional[dict] = None,
    prompt: Optional[str] = None
):
    lang_map = {"ar": "Arabic", "en": "English", "fr": "Français"}
    lang_name = lang_map.get(language.lower(), "Arabic")

    if type == "summary":
        prompt_text = f"Summarize this scientific paper in {lang_name} in clear points:\n{text}"
        return prompt_text, 400
    elif type == "draft":
        spec = document_spec or {}
        doc_type = spec.get("DOCUMENT_TYPE", "Scientific Paper Report")
        target = spec.get("TARGET_AUDIENCE", "Researchers")
        tone = spec.get("TONE", "formal")
        scope = spec.get("CONTENT_SCOPE", "")
        structure = spec.get("STRUCTURE", "")
        references = spec.get("REFERENCES", "")
        prompt_text = (
            f"Create a detailed report in {lang_name} based on the following scientific paper.\n"
            f"DOCUMENT_TYPE: {doc_type}\nTARGET_AUDIENCE: {target}\nTONE: {tone}\n"
            f"CONTENT_SCOPE: {scope}\nSTRUCTURE: {structure}\nREFERENCES: {references}\n\n"
            f"Text:\n{text}"
        )
        return prompt_text, 800
    elif type == "qa":
        prompt_text = f"The following text is from a scientific paper:\n{text}\n\nQuestion: {question}\nAnswer in {lang_name}:"
        return prompt_text, 300
    elif type == "system":
        return prompt or text, 300
    else:
        return text, 300

@app.post("/process-text")
async def process_text_endpoint(
    language: str = Form(...),
    type: str = Form(...),
    text: Optional[str] = Form(None),
    id: Optional[str] = Form(None),
    question: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    document_spec: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    valid_langs = {"ar", "en", "fr"}
    valid_types = {"summary", "draft", "qa", "system"}

    if language.lower() not in valid_langs:
        return JSONResponse({"error": f"Invalid language. Use one of {list(valid_langs)}"}, status_code=400)
    if type.lower() not in valid_types:
        return JSONResponse({"error": f"Invalid type. Must be one of {list(valid_types)}"}, status_code=400)

    if file:
        text = extract_text_from_pdf(file.file)

    if not text and type.lower() != "draft":
        return JSONResponse({"error": "No text provided."}, status_code=400)

    if id and text:
        FILE_STORAGE[id] = text

    doc_spec_dict = None
    if document_spec:
        try:
            doc_spec_dict = json.loads(document_spec)
        except Exception as e:
            return JSONResponse({"error": f"Failed to parse document_spec JSON: {str(e)}"}, status_code=400)

    prompt_text, max_tokens = prepare_prompt(
        type.lower(),
        text,
        language,
        question=question,
        document_spec=doc_spec_dict,
        prompt=prompt
    )

    return StreamingResponse(stream_generate(prompt_text, max_new_tokens=max_tokens), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)