## 1. API для модели машинного обучения (ResNet18), выполняющей классификацию изображений.
## 2. API для LLM через Ollama и ИИ-агент технической поддержки, использующий модель Qwen2.5:1.5B.

### Основные технологии
Python, FastAPI, TorchVision, Ollama, PyTest, GitHub Actions, HTML, TailwindCSS, JavaScript.

### Запуск images_api

```bash
cd image_api
```

```bash
pip install -r requirements.txt
```

```bash
uvicorn app:app --reload
```

### Запуск тестов для image_api

```bash
pytest -v
```

### Запуск llm_api

```bash
cd llm_api
```

```bash
pip install -r requirements.txt
```

```bash
uvicorn app:app --reload
```

### Запуск тестов для image_api

```bash
pytest -v
```