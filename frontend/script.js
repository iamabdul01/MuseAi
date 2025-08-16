console.log("JS loaded");

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM ready");

  const modelEl = document.getElementById("model");
  const promptEl = document.getElementById("prompt");
  const generateBtn = document.getElementById("generate-btn");
  const responseEl = document.getElementById("response");
  const themeToggle = document.getElementById("theme-toggle");
  const up = document.getElementById("thumb-up");
  const down = document.getElementById("thumb-down");

  if (!generateBtn) {
    console.error("❌ generateBtn not found in DOM");
    return;
  }

  // Theme
  themeToggle.addEventListener("click", () => {
    document.documentElement.classList.toggle("dark");
  });

  // Load models
  fetch("/models")
    .then(r => r.json())
    .then(models => {
      modelEl.innerHTML = "";
      (Array.isArray(models) ? models : models.models || []).forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.id;
        opt.textContent = m.name;
        modelEl.appendChild(opt);
      });
    })
    .catch(err => {
      console.error(err);
      modelEl.innerHTML = `<option disabled>Error loading models</option>`;
    });

  // Generate
  generateBtn.addEventListener("click", () => {
    console.log("Generate button clicked!");

    const model = modelEl.value;
    const prompt = (promptEl.value || "").trim();
    if (!prompt) {
      responseEl.textContent = "⚠️ Please enter a prompt.";
      return;
    }

    responseEl.textContent = "Thinking…";

    fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt })
    })
      .then(r => r.json())
      .then(data => {
        if (data.error) {
          responseEl.textContent = `❌ ${data.error}`;
        } else {
          responseEl.textContent = data.response || "(empty response)";
        }
      })
      .catch(err => {
        console.error(err);
        responseEl.textContent = "❌ Network error.";
      });
  });

  // Feedback UI only (no backend yet)
  up.addEventListener("click", () => {
    up.classList.toggle("selected");
    down.classList.remove("selected");
  });
  down.addEventListener("click", () => {
    down.classList.toggle("selected");
    up.classList.remove("selected");
  });
});
