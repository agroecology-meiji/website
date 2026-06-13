document.addEventListener("DOMContentLoaded", async () => {
  const base = "/website";
  const path = window.location.pathname.replace(/\/index\.html$/, "");
  const isEnglish = path === `${base}/en` || path.startsWith(`${base}/en/`);

  await Promise.all([
    loadHTML("#site-header", `${base}/includes/${isEnglish ? "header-en" : "header-ja"}.html`),
    loadHTML("#site-footer", `${base}/includes/${isEnglish ? "footer-en" : "footer-ja"}.html`)
  ]);

  setCurrentNav();
  initFooterYear();
  initEmailTextOnly();
  initNavToggle();
  initSlideshows();
  initReveal();
  protectNoSaveImages();
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
  document.querySelectorAll(`.nav-list a[data-nav="${current}"]`).forEach((link) => link.classList.add("active"));
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
    el.textContent = `${user}@${domain}.${tld}`;
  });
}

function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.textContent = open ? "×" : "☰";
  });
  nav.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.textContent = "☰";
    });
  });
}

function initSlideshows() {
  document.querySelectorAll(".js-slideshow").forEach((slider) => {
    const slides = Array.from(slider.querySelectorAll(".slide"));
    const dots = Array.from(slider.querySelectorAll(".slide-dot"));
    const prev = slider.querySelector("[data-slide-prev]");
    const next = slider.querySelector("[data-slide-next]");
    if (slides.length <= 1) return;
    let index = Math.max(0, slides.findIndex((slide) => slide.classList.contains("is-active")));
    if (index < 0) index = 0;
    let timer = null;
    const interval = Number(slider.dataset.interval || 5200);

    const show = (nextIndex) => {
      index = (nextIndex + slides.length) % slides.length;
      slides.forEach((slide, i) => slide.classList.toggle("is-active", i === index));
      dots.forEach((dot, i) => {
        dot.classList.toggle("is-active", i === index);
        dot.setAttribute("aria-selected", String(i === index));
      });
    };
    const stop = () => { if (timer) window.clearInterval(timer); timer = null; };
    const start = () => {
      if (slider.dataset.autoplay === "false" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      stop();
      timer = window.setInterval(() => show(index + 1), interval);
    };

    prev?.addEventListener("click", () => { show(index - 1); start(); });
    next?.addEventListener("click", () => { show(index + 1); start(); });
    dots.forEach((dot, i) => dot.addEventListener("click", () => { show(i); start(); }));
    slider.addEventListener("mouseenter", stop);
    slider.addEventListener("mouseleave", start);
    slider.addEventListener("focusin", stop);
    slider.addEventListener("focusout", start);
    show(index);
    start();
  });
}

function initReveal() {
  const targets = document.querySelectorAll(".reveal");
  if (!targets.length) return;
  if (!("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  targets.forEach((el) => observer.observe(el));
}

function protectNoSaveImages() {
  document.addEventListener("contextmenu", (event) => {
    if (event.target.closest(".no-save")) event.preventDefault();
  });
  document.addEventListener("dragstart", (event) => {
    if (event.target.closest(".no-save")) event.preventDefault();
  });
}
