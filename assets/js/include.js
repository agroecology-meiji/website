document.addEventListener("DOMContentLoaded", async function () {
  const isEnglishPage = window.location.pathname.includes("/en/");

  const headerFile = isEnglishPage
    ? "/website/includes/header-en.html"
    : "/website/includes/header-ja.html";

  const footerFile = isEnglishPage
    ? "/website/includes/footer-en.html"
    : "/website/includes/footer-ja.html";

  async function loadHTML(selector, file) {
    const element = document.querySelector(selector);
    if (!element) return;

    try {
      const response = await fetch(file);
      if (!response.ok) {
        throw new Error(`Failed to load ${file}`);
      }
      element.innerHTML = await response.text();
    } catch (error) {
      console.error(error);
    }
  }

  await loadHTML("#header-placeholder", headerFile);
  await loadHTML("#footer-placeholder", footerFile);
});