// Page transitions: an A320 flight deck powers up while the next page loads.
// Clicking a link to another page of the site plays a short boot sequence
// (screens test and come alive, thrust levers advance, a loading bar fills),
// then navigates. The next page opens out of the same cockpit.
// Skipped entirely with prefers-reduced-motion. Art: images/pixel/cockpit.png.

window.cockpitLoader = (() => {
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const W = 320;
  const H = 180;
  const DURATION = 1500;
  const ARRIVE_KEY = "cp-arrive";

  // Screen rectangles (x, y, w, h); keep in sync with COCKPIT_SCREENS in tools/pixel/scenes.py.
  const SCREENS = {
    pfdL: [97, 95, 18, 16], ndL: [117, 95, 17, 16],
    ecamU: [151, 94, 18, 17], ecamL: [151, 113, 18, 17],
    ndR: [186, 95, 17, 16], pfdR: [205, 95, 18, 16],
    stby: [142, 101, 6, 7],
    mcduL: [134, 133, 13, 6], mcduR: [173, 133, 13, 6],
  };
  const LEVERS = [152, 165]; // thrust lever x positions; handles travel from y 170 (idle) to 150 (TOGA)

  const DESTINATIONS = {
    "index.html": "Departures hall",
    "developer.html": "Gate D1 / Full-stack developer",
    "photography.html": "Gate P2 / Photography",
    "pilot.html": "Gate A3 / Aspiring airline pilot",
  };

  const art = new Image();
  const artReady = new Promise((resolve) => {
    art.onload = () => resolve(true);
    art.onerror = () => resolve(false);
  });
  art.src = "images/pixel/cockpit.png";

  let overlay = null;
  let busy = false;

  // Drawing ---------------------------------------------------------------

  function px(ctx, x, y, w, h, colour) {
    ctx.fillStyle = colour;
    ctx.fillRect(x, y, w, h);
  }

  // Each screen boots in turn: off, a brief self-test flash, then live content.
  function bootState(index, p) {
    const start = 0.06 + index * 0.05;
    if (p < start) return "off";
    if (p < start + 0.1) return "test";
    return "on";
  }

  function pfd(ctx, [x, y, w, h], t) {
    const horizon = y + Math.round(h / 2 + Math.sin(t / 700) * 1.2);
    px(ctx, x, y, w, horizon - y, "#2f7ae0");
    px(ctx, x, horizon, w, y + h - horizon, "#b0632a");
    px(ctx, x + 3, horizon, w - 6, 1, "#ffffff");
    px(ctx, x, y, 3, h, "#4a4f5c");
    px(ctx, x + w - 3, y, 3, h, "#4a4f5c");
    for (let k = y + 2; k < y + h - 1; k += 3) {
      px(ctx, x + 2, k, 1, 1, "#ffffff");
      px(ctx, x + w - 3, k, 1, 1, "#ffffff");
    }
    const cx = x + Math.floor(w / 2);
    const cy = y + Math.floor(h / 2);
    px(ctx, cx - 5, cy, 3, 1, "#ffd23f");
    px(ctx, cx + 3, cy, 3, 1, "#ffd23f");
    px(ctx, cx, cy, 1, 1, "#ffd23f");
    px(ctx, x + 4, y, w - 8, 2, "#0a0c10");
    px(ctx, x + 5, y, 2, 1, "#3cdc6c");
    px(ctx, x + 9, y, 2, 1, "#ffffff");
    px(ctx, x + 4, y + h - 2, w - 8, 2, "#0a0c10");
  }

  function nd(ctx, [x, y, w, h], t) {
    px(ctx, x, y, w, h, "#05070a");
    const cx = x + w / 2;
    const cy = y + h - 2;
    const r = h - 4;
    for (let a = 200; a <= 340; a += 6) {
      const rad = (a * Math.PI) / 180;
      px(ctx, Math.round(cx + Math.cos(rad) * r), Math.round(cy + Math.sin(rad) * r), 1, 1, "#ffffff");
      px(ctx, Math.round(cx + Math.cos(rad) * (r - 6)), Math.round(cy + Math.sin(rad) * (r - 6)), 1, 1, "#2a8a4a");
    }
    // Heading bug sweeping slowly, magenta route, yellow aircraft symbol.
    const sweep = ((t / 40) % 140) + 200;
    const s = (sweep * Math.PI) / 180;
    px(ctx, Math.round(cx + Math.cos(s) * r), Math.round(cy + Math.sin(s) * r), 1, 1, "#3cdc6c");
    for (let k = 2; k < r - 2; k += 2) px(ctx, Math.round(cx + k * 0.25), cy - k, 1, 1, "#e04bd6");
    px(ctx, Math.round(cx) - 2, cy - 1, 5, 1, "#ffd23f");
    px(ctx, Math.round(cx), cy - 3, 1, 3, "#ffd23f");
    px(ctx, x + w - 5, y + 1, 3, 1, "#3cdc6c");
  }

  function ecamUpper(ctx, [x, y, w, h], p) {
    px(ctx, x, y, w, h, "#05070a");
    // Two engine gauges: green arcs with needles rising as thrust comes up.
    for (const gx of [x + 5, x + 13]) {
      const gy = y + 6;
      for (let a = 180; a <= 360; a += 30) {
        const rad = (a * Math.PI) / 180;
        px(ctx, Math.round(gx + Math.cos(rad) * 4), Math.round(gy + Math.sin(rad) * 4), 1, 1, "#3cdc6c");
      }
      const needle = Math.PI * (1 + 0.15 + p * 0.75);
      for (let k = 0; k <= 3; k++) {
        px(ctx, Math.round(gx + Math.cos(needle) * k), Math.round(gy + Math.sin(needle) * k), 1, 1, "#ffffff");
      }
    }
    for (const [row, len, colour] of [[10, 7, "#3cdc6c"], [12, 11, "#ffffff"], [14, 5, "#3cdc6c"]]) {
      px(ctx, x + 2, y + row, Math.round(len * Math.min(1, p * 1.6)), 1, colour);
    }
  }

  function ecamLower(ctx, [x, y, w, h], p) {
    px(ctx, x, y, w, h, "#05070a");
    for (const [row, len] of [[2, 9], [4, 13], [6, 7]]) px(ctx, x + 2, y + row, len, 1, "#3cdc6c");
    // Loading bar.
    px(ctx, x + 2, y + h - 6, w - 4, 1, "#ffffff");
    px(ctx, x + 2, y + h - 3, w - 4, 1, "#ffffff");
    px(ctx, x + 2, y + h - 5, 1, 2, "#ffffff");
    px(ctx, x + w - 3, y + h - 5, 1, 2, "#ffffff");
    px(ctx, x + 3, y + h - 5, Math.round((w - 6) * p), 2, "#3cdc6c");
  }

  function stby(ctx, [x, y, w, h]) {
    px(ctx, x, y, w, Math.ceil(h / 2), "#2f7ae0");
    px(ctx, x, y + Math.ceil(h / 2), w, Math.floor(h / 2), "#b0632a");
    px(ctx, x + 2, y + 3, 2, 1, "#ffd23f");
  }

  function mcdu(ctx, [x, y, w, h], p, seed) {
    px(ctx, x, y, w, h, "#030605");
    const lines = [[0, 9], [2, 12], [4, 7]];
    lines.forEach(([row, len], i) => {
      const shown = Math.max(0, Math.min(len, Math.round((p * 1.8 - i * 0.25) * len)));
      px(ctx, x + 1, y + row, shown, 1, (i + seed) % 2 ? "#3cdc6c" : "#ffffff");
    });
  }

  function drawFrame(ctx, p, t) {
    ctx.drawImage(art, 0, 0);
    const order = [["pfdL", pfd], ["ndL", nd], ["ecamU", null], ["ecamL", null], ["ndR", nd], ["pfdR", pfd], ["stby", null]];
    order.forEach(([key, fn], i) => {
      const r = SCREENS[key];
      const state = bootState(i, p);
      if (state === "off") return;
      if (state === "test") {
        px(ctx, r[0], r[1], r[2], r[3], i % 2 ? "#e8f0ff" : "#3cdc6c");
        return;
      }
      if (fn) fn(ctx, r, t);
      else if (key === "ecamU") ecamUpper(ctx, r, p);
      else if (key === "ecamL") ecamLower(ctx, r, p);
      else stby(ctx, r);
    });
    mcdu(ctx, SCREENS.mcduL, p, 0);
    mcdu(ctx, SCREENS.mcduR, p, 1);

    // Thrust levers advance from idle to TOGA with the loading progress.
    const handleY = Math.round(170 - 20 * p);
    for (const lx of LEVERS) {
      px(ctx, lx + 1, handleY + 3, 2, 178 - handleY - 3, "#9aa0ac");
      px(ctx, lx, handleY, 4, 3, "#121318");
      px(ctx, lx, handleY, 4, 1, "#3a3d48");
    }
  }

  // Overlay -----------------------------------------------------------------

  function build(label) {
    const el = document.createElement("div");
    el.className = "cockpit-loader";
    el.setAttribute("role", "status");
    const canvas = document.createElement("canvas");
    canvas.width = W;
    canvas.height = H;
    canvas.setAttribute("aria-hidden", "true");
    const caption = document.createElement("p");
    caption.className = "cockpit-caption";
    caption.innerHTML = `<span class="readout">Now boarding</span> <strong></strong>`;
    caption.querySelector("strong").textContent = label;
    el.append(canvas, caption);
    document.body.append(el);

    // Full screen: the smallest whole-number scale that covers the whole viewport
    // (whole numbers keep the pixels square). The overflow is cropped evenly, so
    // narrow phone screens show the centre of the flight deck.
    const scale = Math.max(1, Math.ceil(Math.max(innerWidth / W, innerHeight / H)));
    canvas.style.width = `${W * scale}px`;
    canvas.style.height = `${H * scale}px`;
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = false;
    return { el, ctx };
  }

  function labelFor(url) {
    const file = url.pathname.split("/").pop() || "index.html";
    return DESTINATIONS[file] || null;
  }

  async function go(href) {
    const url = new URL(href, location.href);
    if (reduceMotion || busy) {
      if (!busy) location.href = url.href;
      return;
    }
    busy = true;
    if (!(await artReady)) {
      location.href = url.href;
      return;
    }
    window.sfx?.play("start");
    overlay = build(labelFor(url) || "Next gate");
    const start = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - start) / DURATION);
      drawFrame(overlay.ctx, 1 - (1 - p) ** 2, now);
      if (p < 1) {
        requestAnimationFrame(step);
        return;
      }
      try { sessionStorage.setItem(ARRIVE_KEY, "1"); } catch { /* storage blocked: no arrival effect */ }
      location.href = url.href;
    };
    requestAnimationFrame(step);
  }

  // Arriving from another page: start inside the cockpit, then open out.
  async function arrive() {
    const root = document.documentElement;
    if (!root.classList.contains("cockpit-arriving")) return;
    try { sessionStorage.removeItem(ARRIVE_KEY); } catch { /* ignore */ }
    if (reduceMotion || !(await artReady)) {
      root.classList.remove("cockpit-arriving");
      return;
    }
    const shown = build(labelFor(location) || "");
    drawFrame(shown.ctx, 1, performance.now());
    root.classList.remove("cockpit-arriving");
    setTimeout(() => shown.el.classList.add("is-leaving"), 200);
    setTimeout(() => shown.el.remove(), 750);
  }

  // Intercept ordinary clicks on links to the site's own pages.
  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest?.("a[href]");
    if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || !labelFor(url)) return;
    if (url.pathname === location.pathname && url.hash) return;
    event.preventDefault();
    go(url.href);
  });

  // Coming back with the browser's back button can restore this page from cache
  // with the overlay still showing; clear it.
  addEventListener("pageshow", (event) => {
    if (!event.persisted) return;
    overlay?.el.remove();
    overlay = null;
    busy = false;
  });

  arrive();

  return { go };
})();
