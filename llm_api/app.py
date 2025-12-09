import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from langfuse import Langfuse
import tiktoken  
import time 
import hashlib 
from fastapi import FastAPI, Request, File, UploadFile



load_dotenv()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

lf_client = Langfuse(secret_key=LANGFUSE_SECRET_KEY)

app = FastAPI(title="LLM API via Ollama")
OLLAMA_URL = "http://localhost:11434/api/generate"
THRESHOLD = 0.7

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "../image_api/static"))
INDEX_PATH = os.path.join(STATIC_DIR, "index.html")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PromptRequest(BaseModel):
    model: str = "qwen2.5:1.5b"
    prompt: str
    prompt_version: str = "v1"

class AgentRequest(BaseModel):
    model: str = "qwen2.5:1.5b"
    prompt: str
    prompt_version: str = "v1"

def count_tokens(prompt: str, model: str) -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(prompt))

def call_llm_logged(model: str, prompt: str, prompt_version: str = "v1") -> str:
    event = lf_client.event(
        name="llm_call",
        input=prompt,
        metadata={"model": model, "prompt_version": prompt_version}
    )
    start_time = time.time()
    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        result = data.get("response", "").strip()

        input_tokens = len(prompt.split())
        output_tokens = len(result.split())
        latency = time.time() - start_time

        event.update(
            output=result,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency": latency,
                "response_hash": hashlib.sha256(result.encode()).hexdigest()
            }
        )
        event.end()
        return result

    except Exception as e:
        event.update(
            metadata={"error": str(e), "latency": time.time() - start_time}
        )
        event.end()
        raise

def decide(prompt: str, model: str = "qwen2.5:1.5b", prompt_version: str = "v1"):
    classification_prompt = f"""
    Классификатор обращений в IT-поддержку.
    Запрос: "{prompt}"
    Ответь в формате категория;уверенность
    """
    resp = call_llm_logged(model, classification_prompt, prompt_version)
    try:
        label, conf_str = resp.split(";")
        label = label.strip()
        conf = float(conf_str.strip())
    except Exception:
        label = "other"
        conf = 0.0

    if conf >= THRESHOLD:
        advice_prompt = f"Запрос: '{prompt}', категория {label}. Дай краткий план."
        advice = call_llm_logged(model, advice_prompt, prompt_version)
        return {"action": "answer", "label": label, "text": advice, "confidence": conf}
    else:
        clarify_prompt = f"Запрос: '{prompt}'. Задай 2-3 уточняющих вопроса."
        clar = call_llm_logged(model, clarify_prompt, prompt_version)
        return {"action": "clarify", "label": label, "text": clar, "confidence": conf}


@app.middleware("http")
async def add_langfuse_trace(request: Request, call_next):
    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        event = lf_client.event(
            name="http_request",
            input={"path": request.url.path, "method": request.method}
        )
    else:
        body = await request.body()
        try:
            body = body.decode("utf-8")
        except:
            body = "<binary>"
        
        event = lf_client.event(
            name="http_request",
            input={"path": request.url.path, "method": request.method, "body": body}
        )

    start_time = time.time()

    try:
        response = await call_next(request)
        event.update(metadata={"status_code": response.status_code, "latency": time.time() - start_time})
        event.end()
        return response

    except Exception as e:
        event.update(metadata={"error": str(e), "latency": time.time() - start_time})
        event.end()
        raise


@app.get("/")
def read_root():
    return FileResponse(INDEX_PATH)

@app.post("/generate")
def generate_text(request: PromptRequest):
    try:
        response_text = call_llm_logged(
            request.model, request.prompt, request.prompt_version
        )
        return {"model": request.model, "response": response_text}
    except Exception as e:
        return {"error": f"Ошибка запроса к Ollama: {str(e)}"}

@app.post("/agent")
def agent_endpoint(request: AgentRequest):
    try:
        result = decide(
            request.prompt, model=request.model, prompt_version=request.prompt_version
        )
        return result
    except Exception as e:
        return {"error": f"Ошибка работы агента: {str(e)}"}
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    return {"status": "ok"}