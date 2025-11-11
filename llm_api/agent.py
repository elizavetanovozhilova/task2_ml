from llm_api import api_client  # небольшой wrapper вокруг /generate
THRESHOLD = 0.7

def decide(prompt):
    classification_prompt = f"Классифицируй запрос: '{prompt}' в одном слове: network/software/hardware/other. Также дай оценку уверенности 0-1."
    resp = api_client.generate(model="qwen2.5:1.5b", prompt=classification_prompt)
    label, conf = resp.split(";")
    conf = float(conf)
    if conf >= THRESHOLD:
        advice = api_client.generate(model="qwen2.5:1.5b",
                                    prompt=f"Для запроса '{prompt}' дай краткий пошаговый план решения если это {label}.")
        return {"action":"answer","text":advice,"confidence":conf}
    else:
        clar = api_client.generate(model="qwen2.5:1.5b",
                                  prompt=f"Для уточнения запроса '{prompt}' задай 2 уточняющих вопроса.")
        return {"action":"clarify","text":clar,"confidence":conf}
