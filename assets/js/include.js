document.addEventListener("DOMContentLoaded", async () => {
  const base = "/website";
  const path = window.location.pathname.replace(/\/index\.html$/, "");

  const isEnglish =
    path === `${base}/en` ||
    path.startsWith(`${base}/en/`);

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
  initEmailTextOnly();
  initNavToggle();
});

async function loadHTML(selector, file) {
  const target = document.querySelector(selector);
  if (!target) return;

  try {
    const response = await fetch(file);
    if (!response.ok) throw new Error(`Failed to load ${file}`);
    target.innerHTML = await response.text();
  } catch (error) {
    console.error(error);
  }
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

  const link = document.querySelector(`.nav-list a[data-nav="${current}"]`);
  if (link) link.classList.add("active");
}

function initFooterYear() {
  const y = document.getElementById("y");
  if (y) y.textContent = new Date().getFullYear();
}

function initEmailTextOnly() {
  document.querySelectorAll(".js-email").forEach((el) => {
    const user = el.getAttribute("data-user") || "";
    const domain = el.getAttribute("data-domain") || "";
    const tld = el.getAttribute("data-tld") || "";

    if (!user || !domain || !tld) return;

    const addr = `${user}@${domain}.${tld}`;
    el.textContent = addr;
  });
}

function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");

  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
  });
}

document.addEventListener("contextmenu", (event) => {
  if (event.target.classList.contains("no-save")) {
    event.preventDefault();
  }
});

document.addEventListener("dragstart", (event) => {
  if (event.target.classList.contains("no-save")) {
    event.preventDefault();
  }
});
