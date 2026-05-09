document.addEventListener("DOMContentLoaded", async () => {
  const base = "/website";
  const path = window.location.pathname;
  const isEnglish = path.includes("/en/");

  const headerFile = isEnglish
    ? `${base}/includes/header-en.html`
    : `${base}/includes/header-ja.html`;

  const footerFile = isEnglish
    ? `${base}/includes/footer-en.html`
    : `${base}/includes/footer-ja.html`;

  await Promise.all([
    loadHTML("#site-header", headerFile),
    loadHTML("#site-footer", footerFile)
  ]);

  setCurrentNav();
  initFooterYear();
  initEmail();
  initNavToggle();
});

async function loadHTML(selector, file) {
  const target = document.querySelector(selector);
  if (!target) return;

  const response = await fetch(file);
  if (!response.ok) {
    console.error(`Failed to load ${file}`);
    return;
  }

  target.innerHTML = await response.text();
}

function setCurrentNav() {
  const path = window.location.pathname.replace(/\/index\.html$/, "/");

  let current = "home";

  if (path.includes("/researches/")) current = "researches";
  else if (path.includes("/members/")) current = "members";
  else if (path.includes("/news/")) current = "news";
  else if (path.includes("/publications/")) current = "publications";
  else if (path.includes("/contact/")) current = "contact";
  else if (path.includes("/gallery/")) current = "gallery";

  const link = document.querySelector(`[data-nav="${current}"]`);
  if (link) link.classList.add("active");
}

function initFooterYear() {
  const year = document.querySelector("#y");
  if (year) {
    year.textContent = new Date().getFullYear();
  }
}

function initEmail() {
  document.querySelectorAll(".js-email").forEach((el) => {
    const user = el.dataset.user;
    const domain = el.dataset.domain;
    const tld = el.dataset.tld;

    if (!user || !domain || !tld) return;

    const email = `${user}@${domain}.${tld}`;
    el.innerHTML = `<a href="mailto:${email}">${email}</a>`;
  });
}

function initNavToggle() {
  const button = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");

  if (!button || !nav) return;

  button.addEventListener("click", () => {
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!expanded));
    nav.classList.toggle("open");
  });
}