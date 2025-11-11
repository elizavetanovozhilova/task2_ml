from fastapi import FastAPI
from pydantic import BaseModel
import requests
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="LLM API via Ollama")

OLLAMA_URL = "http://localhost:11434/api/generate"


class PromptRequest(BaseModel):
    model: str = "qwen2.5:1.5b"
    prompt: str

class AgentRequest(BaseModel):
    model: str = "qwen2.5:1.5b"
    prompt: str



def call_llm(model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()



THRESHOLD = 0.7

def decide(prompt: str, model: str = "qwen2.5:1.5b"):
    classification_prompt = f"""
    Ты — классификатор обращений в IT-поддержку.

    Нужно отнести запрос пользователя к одной из категорий:
    - network  (всё, что связано с Wi-Fi, интернетом, сетью)
    - software (приложения, программы, операционная система)
    - hardware (железо: ноутбук, монитор, мышь, клавиатура и т.п.)
    - other    (если ничего из выше перечисленного)

    Запрос пользователя: "{prompt}"

    1) Определи ОДНУ категорию (network/software/hardware/other).
    2) Оцени свою уверенность числом от 0 до 1 (например, 0.85).

    Ответь СТРОГО в формате:
    категория;уверенность

    Примеры корректных ответов:
    network;0.92
    software;0.7
    hardware;0.8
    other;0.4
    """

    resp = call_llm(model, classification_prompt)
    try:
        label, conf_str = resp.split(";")
        label = label.strip()
        conf = float(conf_str.strip())
    except Exception:
        label = "other"
        conf = 0.0

    if conf >= THRESHOLD:
        advice_prompt = (
            f"Пользовательский запрос: '{prompt}'. "
            f"Считаем, что это категория {label}. "
            f"Дай краткий пошаговый план решения проблемы, нумерованный списком."
        )
        advice = call_llm(model, advice_prompt)
        return {"action": "answer", "label": label, "text": advice, "confidence": conf}
    else:
        clarify_prompt = (
            f"Пользовательский запрос: '{prompt}'. "
            f"Ты не уверен в категории. Задай 2–3 уточняющих вопроса, "
            f"чтобы лучше понять проблему. Ответь только вопросами."
        )
        clar = call_llm(model, clarify_prompt)
        return {"action": "clarify", "label": label, "text": clar, "confidence": conf}



@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.post("/generate")
def generate_text(request: PromptRequest):
    try:
        response_text = call_llm(request.model, request.prompt)
        return {"model": request.model, "response": response_text}
    except Exception as e:
        return {"error": f"Ошибка запроса к Ollama: {str(e)}"}


@app.post("/agent")
def agent_endpoint(request: AgentRequest):
    try:
        result = decide(request.prompt, model=request.model)
        return result
    except Exception as e:
        return {"error": f"Ошибка работы агента: {str(e)}"}



app.mount("/static", StaticFiles(directory="static"), name="static")
