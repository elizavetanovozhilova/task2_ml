document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("fileInput");
  const resultDiv = document.getElementById("result");

  if (!fileInput.files.length) {
    alert("Выберите изображение.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  resultDiv.innerHTML = "<p class='text-gray-500'>Обработка изображения...</p>";

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Ошибка при запросе к API");
    }

    const data = await response.json();
    const preds = data.predictions;

    let html = "<h2 class='text-lg font-semibold mb-2'>Результаты:</h2><ul>";
    preds.forEach(p => {
      html += `<li>${p.class}: <strong>${(p.probability * 100).toFixed(2)}%</strong></li>`;
    });
    html += "</ul>";

    resultDiv.innerHTML = html;
  } catch (err) {
    resultDiv.innerHTML = `<p class='text-red-500'>Ошибка: ${err.message}</p>`;
  }
});
