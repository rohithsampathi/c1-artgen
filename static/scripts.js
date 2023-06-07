function updateElapsedTime(startTime) {
  const elapsedTimeElement = document.getElementById("elapsed-time-value");
  const currentTime = new Date();
  const elapsedTime = Math.floor((currentTime - startTime) / 1000);
  elapsedTimeElement.textContent = elapsedTime;
}

function adjustHeight(element, defaultHeight) {
  element.style.height = defaultHeight; // Reset element height in case of decreasing text lines
  element.style.height = `${element.scrollHeight}px`; // Set element height equal to scroll height
}

const dynamicHeightInputs = Array.from(document.getElementsByClassName("dynamic-height"));
dynamicHeightInputs.forEach(input => {
  // Apply the height adjustment when the input changes
  input.addEventListener('input', () => adjustHeight(input, '1em'));
  // Initialize the correct height on page load
  adjustHeight(input, '1em');
});

const generateBtn = document.getElementById("generate-btn");
if (generateBtn) {
  generateBtn.addEventListener("click", async event => {
    event.preventDefault();

    const newsInput = document.getElementById("news-input");
    const newsOutput = document.getElementById("news-output");
    const loader = document.getElementById("loader");
    const elapsedTimeContainer = document.getElementById("elapsed-time-container");

    if (!newsInput.value) {
      alert("Please enter a valid URL before generating the post.");
      return;
    }

    loader.classList.remove("hidden");
    elapsedTimeContainer.classList.remove("hidden");

    const startTime = new Date();
    updateElapsedTime(startTime);
    const elapsedTimeInterval = setInterval(() => updateElapsedTime(startTime), 1000);

    const formData = new FormData();
    formData.append("news", newsInput.value);
    formData.append("search_terms", document.getElementById("search-terms-input").value);
    formData.append("theme", document.getElementById("theme-input").value);

    try {
      const response = await fetch("/generate", { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error ? data.error : "Network response was not ok");
      }
      loader.classList.add("hidden");
      clearInterval(elapsedTimeInterval);
      newsOutput.value = data.result.art_output;
    } catch (error) {
      console.error("Error:", error);
      loader.classList.add("hidden");
      elapsedTimeContainer.classList.add("hidden");
      clearInterval(elapsedTimeInterval);
    }
  });
}

const regenerateBtn = document.getElementById("regenerate-btn");
if (regenerateBtn) {
  regenerateBtn.addEventListener("click", () => {
    document.getElementById("news-input").value = "";
    document.getElementById("news-output").value = "";
    generateBtn.click();
  });
}