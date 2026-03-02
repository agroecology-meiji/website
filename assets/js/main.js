(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  document.querySelectorAll('.js-email').forEach((el) => {
    const user = el.getAttribute('data-user') || '';
    const domain = el.getAttribute('data-domain') || '';
    const tld = el.getAttribute('data-tld') || '';
    const addr = `${user}@${domain}.${tld}`;
    const a = document.createElement('a');
    a.href = `mailto:${addr}`;
    a.textContent = addr;
    el.appendChild(a);
  });
})();
