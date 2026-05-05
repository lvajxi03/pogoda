function applyTheme(theme) {
  const isDark = theme === "dark";
  document.documentElement.classList.toggle("dark", isDark);
  localStorage.theme = theme;

  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.textContent = isDark ? "☀️ Tryb jasny" : "🌙 Tryb ciemny";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const savedTheme =
    localStorage.theme ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

  applyTheme(savedTheme);

  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const current = document.documentElement.classList.contains("dark")
        ? "dark"
        : "light";

      applyTheme(current === "dark" ? "light" : "dark");
    });
  }
});

