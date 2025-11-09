from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    """Проверка, что главная страница отдается"""
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()

def test_predict_no_file():
    """Проверка: запрос без файла должен вернуть ошибку"""
    response = client.post("/predict")
    assert response.status_code == 422

def test_predict_with_file():
    """Проверка: API возвращает результат при загрузке изображения"""
    with open("test.jpg", "rb") as f:
        response = client.post("/predict", files={"file": ("test.jpg", f, "image/jpeg")})
    assert response.status_code == 200
    json_data = response.json()
    assert "predictions" in json_data
    assert isinstance(json_data["predictions"], list)
    assert len(json_data["predictions"]) > 0
    assert "class" in json_data["predictions"][0]
    assert "probability" in json_data["predictions"][0]
