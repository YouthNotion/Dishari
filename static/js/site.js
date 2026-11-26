// Dishari: progressive enhancements only. The site is fully usable without JS.
(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function initNav() {
    const toggle = document.querySelector("[data-nav-toggle]");
    const nav = document.querySelector("[data-nav]");
    if (!toggle || !nav) return;

    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };

    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  function initHeaderShadow() {
    const header = document.querySelector("[data-header]");
    if (!header) return;
    const update = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
    update();
    window.addEventListener("scroll", update, { passive: true });
  }

  function initRotatingPhrase() {
    const target = document.querySelector("[data-rotate]");
    const source = document.getElementById("hero-phrases");
    if (!target || !source) return;

    let phrases;
    try {
      phrases = JSON.parse(source.textContent);
    } catch {
      return;
    }
    if (!Array.isArray(phrases) || phrases.length < 2) return;

    target.setAttribute("aria-live", "off"); // avoid noisy screen-reader announcements
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    if (reducedMotion) {
      let i = 0;
      setInterval(() => {
        i = (i + 1) % phrases.length;
        target.textContent = phrases[i];
      }, 4000);
      return;
    }

    (async () => {
      target.classList.add("is-typing");
      let i = 0;
      for (;;) {
        await sleep(2200);
        const current = phrases[i];
        for (let n = current.length; n >= 0; n--) {
          target.textContent = current.slice(0, n);
          await sleep(45);
        }
        i = (i + 1) % phrases.length;
        const next = phrases[i];
        for (let n = 1; n <= next.length; n++) {
          target.textContent = next.slice(0, n);
          await sleep(85);
        }
      }
    })();
  }

  function initThemeToggle() {
    const button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    const root = document.documentElement;
    const systemDark = window.matchMedia("(prefers-color-scheme: dark)");

    const savedTheme = () => {
      try {
        return localStorage.getItem("theme");
      } catch {
        return null;
      }
    };
    const apply = (theme) => {
      root.dataset.theme = theme;
      // role="switch" labelled "Dark theme": checked means dark.
      button.setAttribute("aria-checked", String(theme === "dark"));
    };

    apply(root.dataset.theme === "dark" ? "dark" : "light");
    button.hidden = false;
    // Enable the switch's animations only after its initial state has painted.
    requestAnimationFrame(() => requestAnimationFrame(() => button.classList.add("is-ready")));

    button.addEventListener("click", () => {
      const theme = root.dataset.theme === "dark" ? "light" : "dark";
      apply(theme);
      try {
        localStorage.setItem("theme", theme);
      } catch {
        // Not persisted; the choice still applies for this page view.
      }
    });

    // Follow OS changes until the visitor makes an explicit choice.
    systemDark.addEventListener("change", (event) => {
      if (!savedTheme()) apply(event.matches ? "dark" : "light");
    });
  }

  initThemeToggle();
  initNav();
  initHeaderShadow();
  initRotatingPhrase();
})();
