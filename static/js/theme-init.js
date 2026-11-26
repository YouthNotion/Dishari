// Runs synchronously in <head> (before first paint) so a saved theme never flashes.
// Kept tiny and separate because the CSP forbids inline scripts.
//
// It is also the single source of truth for reading the saved theme: it exposes
// `window.dishariTheme`, which site.js uses, so both scripts always agree on what
// counts as a saved choice (only "light" or "dark"; anything else means "follow the OS").
(() => {
  "use strict";
  const STORAGE_KEY = "theme";
  const VALID = ["light", "dark"];

  /** The visitor's explicit choice, or null if there is none (or it's invalid). */
  const readSavedTheme = () => {
    try {
      const value = localStorage.getItem(STORAGE_KEY);
      return VALID.includes(value) ? value : null;
    } catch {
      return null; // Storage blocked (private mode, etc.): follow the OS preference.
    }
  };

  const systemTheme = () =>
    window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";

  window.dishariTheme = Object.freeze({ STORAGE_KEY, readSavedTheme, systemTheme });
  document.documentElement.dataset.theme = readSavedTheme() ?? systemTheme();
})();
