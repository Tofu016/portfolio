// Departures board: split-flap letters and a local clock.
// Without JS (or with reduced motion) the board simply shows its text.

const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

function randomChar() {
  return CHARS[Math.floor(Math.random() * CHARS.length)];
}

function buildTiles(el) {
  const text = el.textContent.trim();
  const tiles = document.createElement("span");

  tiles.setAttribute("aria-hidden", "true");
  el.textContent = "";
  el.append(tiles);

  // Each word's tiles sit in an unbreakable group, so on narrow screens a long
  // destination ("ASPIRING AIRLINE") wraps between words, never mid-word.
  let word = null;
  return [...text].map((char) => {
    const tile = document.createElement("span");
    tile.className = "tile";
    if (char === " ") {
      tile.textContent = " ";
      tiles.append(tile);
      word = null;
    } else {
      if (!word) {
        word = document.createElement("span");
        word.className = "word";
        tiles.append(word);
      }
      tile.textContent = char;
      word.append(tile);
    }
    return { tile, char };
  });
}

function flap(tiles, rowDelay) {
  tiles.forEach(({ tile, char }, i) => {
    if (char === " ") return;

    const settleAt = performance.now() + 300 + rowDelay + i * 55 + Math.random() * 250;
    const timer = setInterval(() => {
      const done = performance.now() >= settleAt;
      tile.textContent = done ? char : randomChar();
      tile.classList.remove("flip");
      void tile.offsetWidth; // restart the flip animation
      tile.classList.add("flip");
      if (done) clearInterval(timer);
    }, 70);
  });
}

document.querySelectorAll(".board-rows li").forEach((row, rowIndex) => {
  row.querySelectorAll("[data-flap]").forEach((el) => {
    const tiles = buildTiles(el);
    if (!reduceMotion) flap(tiles, rowIndex * 150);
  });
});

const clock = document.querySelector("[data-clock]");

function tick() {
  const now = new Date();
  clock.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
  clock.dateTime = now.toISOString();
}

if (clock) {
  tick();
  setInterval(tick, 15000);
}
