document.getElementById("sendBtn").addEventListener("click", async () => {
  const prompt = document.getElementById("promptInput").value.trim();
  const model = document.getElementById("modelSelect").value;
  const resultDiv = document.getElementById("result");

  if (!prompt) {
    alert("Введите текст запроса для LLM!");
    return;
  }

  resultDiv.innerHTML = "Генерирую ответ от LLM...";

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt })
    });

    if (!response.ok) {
      throw new Error("Ошибка запроса к /generate");
    }

    const data = await response.json();
    if (data.error) {
      resultDiv.innerHTML = data.error;
    } else {
      resultDiv.innerHTML = data.response || "Пустой ответ от модели";
    }
  } catch (err) {
    resultDiv.innerHTML = `Ошибка: ${err.message}`;
  }
});

document.getElementById("agentBtn").addEventListener("click", async () => {
  const prompt = document.getElementById("agentPrompt").value.trim();
  const model = document.getElementById("agentModel").value;
  const resultDiv = document.getElementById("agentResult");

  if (!prompt) {
    alert("Опишите проблему для агента!");
    return;
  }

  resultDiv.innerHTML = "Агент думает над вашим запросом...";

  try {
    const response = await fetch("/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt })
    });

    if (!response.ok) {
      throw new Error("Ошибка запроса к /agent");
    }

    const data = await response.json();
    if (data.error) {
      resultDiv.innerHTML = data.error;
      return;
    }

    const { action, label, text, confidence } = data;

    resultDiv.innerHTML =
      `Действие агента: ${action}\n` +
      `Категория: ${label}\n` +
      `Уверенность: ${(confidence * 100).toFixed(1)}%\n\n` +
      `Ответ:\n${text}`;
  } catch (err) {
    resultDiv.innerHTML = `Ошибка: ${err.message}`;
  }
});
