// Typewriter text for the RPG-style dialog boxes on the subpages.
// The full text stays in the DOM for screen readers; only the visible copy types out.

(() => {
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const CHARS_PER_SECOND = 45;

  document.querySelectorAll("[data-type]").forEach((el) => {
    if (reduceMotion) return;

    const text = el.textContent.trim();
    const sr = document.createElement("span");
    const shown = document.createElement("span");

    sr.className = "visually-hidden";
    sr.textContent = text;
    shown.setAttribute("aria-hidden", "true");
    el.textContent = "";
    el.append(sr, shown);

    // Reserve the final height so the layout doesn't jump while typing.
    el.style.minHeight = `${el.offsetHeight}px`;
    shown.textContent = text;
    const height = el.offsetHeight;
    shown.textContent = "";
    el.style.minHeight = `${height}px`;

    let i = 0;
    let timer = null;

    function finish() {
      clearInterval(timer);
      shown.textContent = text;
      el.classList.add("is-done");
    }

    timer = setInterval(() => {
      i += 1;
      shown.textContent = text.slice(0, i);
      if (i % 3 === 0) window.sfx?.play("text");
      if (i >= text.length) finish();
    }, 1000 / CHARS_PER_SECOND);

    // Click the box to skip the typing.
    el.closest(".dialog-box")?.addEventListener("click", finish);
  });
})();
