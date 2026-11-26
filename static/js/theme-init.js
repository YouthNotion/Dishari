// Runs synchronously in <head> (before first paint) so a saved theme never flashes.
// Kept tiny and separate because the CSP forbids inline scripts.
(() => {
  "use strict";
  let saved = null;
  try {
    saved = localStorage.getItem("theme");
  } catch {
    // Storage blocked (private mode, etc.): fall back to the OS preference.
  }
  const theme =
    saved === "light" || saved === "dark"
      ? saved
      : window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
  document.documentElement.dataset.theme = theme;
})();
