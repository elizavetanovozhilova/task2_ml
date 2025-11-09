## Веб-интерфейс

Приложение имеет простой веб-фронтенд для тестирования модели.

### Запуск images_api

```bash
cd image_api
```

```bash
uvicorn app:app --reload
```

### Запуск тестов для image_api

```bash
pytest -v
```