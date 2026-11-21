// Terminal CP: a small side-scrolling game on the main page.
// Walk through the concourse and board a gate to open a page.
// Everything here is an enhancement: without JS the page shows a static scene
// and the departures board below works as the plain menu.

(() => {
  const root = document.getElementById("game");
  if (!root) return;

  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const LEVEL_W = 1440;
  const H = 168;
  const FEET = 150;
  const SPEED = 72;
  const REACH = 22;

  // Positions must match tools/pixel/scenes.py (INFO_X and GATES).
  const ZONES = [
    { x: 520, kind: "desk", label: "Talk" },
    { x: 760, kind: "gate", label: "Board", href: "developer.html", flight: "CP 101", dest: "FULL-STACK DEVELOPER", gate: "D1" },
    { x: 1000, kind: "gate", label: "Board", href: "photography.html", flight: "CP 202", dest: "PHOTOGRAPHY", gate: "P2" },
    { x: 1240, kind: "gate", label: "Board", href: "pilot.html", flight: "CP 303", dest: "ASPIRING AIRLINE PILOT", gate: "A3" },
  ];

  const $ = (sel) => root.querySelector(sel);
  const title = $(".game-title");
  const startBtn = $(".game-start");
  const dialog = $(".game-dialog");
  const lineEl = $(".game-line");
  const srEl = $(".game-sr");
  const choicesEl = $(".game-choices");
  const prompt = $(".game-prompt");
  const viewport = $(".game-view");

  const canvas = document.createElement("canvas");
  canvas.className = "game-canvas";
  canvas.setAttribute("aria-hidden", "true");
  const ctx = canvas.getContext("2d");

  const img = {};
  const player = { x: 120, dir: 1, frame: 0, clock: 0, target: null, after: null };
  const keys = new Set();
  // Background life (planes and people) comes from the shared airport.js module.
  const A = window.Airport;
  const traffic = A.createTraffic({ rollY: 75, taxiY: 86, levelW: LEVEL_W });
  const crowd = A.createCrowd({
    sheet: "crowd",
    rows: 8,
    walkers: 12,
    lanes: [138, 142, 146, 153, 157, 161],
    maxX: LEVEL_W,
    // Queues at both check-in islands, one at the info desk, one watching planes.
    standers: [[140, 132], [158, 132], [320, 132], [338, 132], [546, 126], [1132, 126]]
      .map(([x, feet], i) => ({ x, feet, row: i % 8, flip: i === 5 })),
  });
  // Airline crews: two crews walking to and from the gates, plus crew waiting at gates.
  // flight-crew.png rows: 0 captain, 1 first officer, 2 attendant (red), 3 attendant (navy).
  const flightCrew = A.createCrowd({
    sheet: "flight-crew",
    rows: 4,
    maxX: LEVEL_W,
    groups: [
      { rows: [0, 1, 2, 3], x: 260, feet: 149, v: 13, gap: 15 },
      { rows: [1, 0, 3, 2], x: 1180, feet: 155, v: -12, gap: 15 },
    ],
    standers: [
      { x: 806, feet: 128, row: 2 },
      { x: 819, feet: 128, row: 3, flip: true },
      { x: 1222, feet: 127, row: 0 },
    ],
  });
  const view = { ctx, cam: 0, viewW: 0 };

  // Speech bubbles: travellers (kids are crowd rows 6-7) and crew (rows 0-1 pilots, 2-3 attendants).
  const chatter = A.createChatter({
    host: viewport,
    canvas,
    speakers: () => [
      ...crowd.people.map((p) => ({ person: p, h: 20, lines: p.row >= 6 ? A.LINES.kids : A.LINES.travellers })),
      ...flightCrew.people.map((p) => ({ person: p, h: 20, lines: p.row < 2 ? A.LINES.pilots : A.LINES.attendants })),
    ],
  });

  let scale = 2;
  let viewW = 0;
  let cam = 0;
  let state = "title"; // title | play | dialog
  let near = null;
  let last = 0;
  let visible = true;
  let talk = null;

  // Loading and sizing ---------------------------------------------------

  function resize() {
    scale = innerWidth >= 1500 ? 3 : 2;
    viewW = Math.min(LEVEL_W, Math.floor(viewport.clientWidth / scale));
    canvas.width = viewW;
    canvas.height = H;
    canvas.style.width = `${viewW * scale}px`;
    canvas.style.height = `${H * scale}px`;
    root.style.setProperty("--s", scale);
    ctx.imageSmoothingEnabled = false;
    draw();
  }

  // Drawing ---------------------------------------------------------------

  function draw() {
    if (!img["concourse-sky"]) return;
    view.cam = cam;
    view.viewW = viewW;
    ctx.drawImage(img["concourse-sky"], cam, 0, viewW, H, 0, 0, viewW, H);
    traffic.drawPlanes(view, img);
    ctx.drawImage(img["concourse-apron"], cam, 0, viewW, H, 0, 0, viewW, H);
    traffic.drawTaxi(view, img);
    ctx.drawImage(img["concourse-front"], cam, 0, viewW, H, 0, 0, viewW, H);

    // People and the player, nearest last.
    const cast = [...crowd.cast(view, img), ...flightCrew.cast(view, img)];
    cast.push({ feet: FEET, draw: () => A.sprite(view, img.player, player.frame, 16, 32, player.x - 8, FEET - 32, player.dir < 0) });
    cast.sort((a, b) => a.feet - b.feet);
    cast.forEach((c) => c.draw());

    if (near && state === "play") {
      prompt.hidden = false;
      prompt.textContent = `▲ ${near.label}`;
      prompt.style.left = `${canvas.offsetLeft + (near.x - cam) * scale}px`;
    } else {
      prompt.hidden = true;
    }
  }

  // Simulation ------------------------------------------------------------

  function update(dt) {
    if (!reduceMotion) {
      traffic.update(dt, { cam, viewW });
      crowd.update(dt);
      flightCrew.update(dt);
    }
    // Only chat while you're playing (not on the title screen or during a dialog).
    chatter.update(dt, { cam, viewW }, scale, state === "play");

    if (state !== "play") return;

    let dir = 0;
    if (keys.has("left")) dir -= 1;
    if (keys.has("right")) dir += 1;
    if (dir) {
      player.target = null;
      player.after = null;
    } else if (player.target !== null) {
      const gap = player.target - player.x;
      if (Math.abs(gap) < 1.5) {
        player.x = player.target;
        player.target = null;
        const after = player.after;
        player.after = null;
        if (after) interact(after);
      } else {
        dir = Math.sign(gap);
      }
    }

    if (dir) {
      player.x = Math.min(LEVEL_W - 16, Math.max(16, player.x + dir * SPEED * dt));
      player.dir = dir;
      player.clock += dt;
      player.frame = 1 + (Math.floor(player.clock / 0.12) % 4);
    } else {
      player.frame = 0;
      player.clock = 0;
    }

    cam = Math.round(Math.min(LEVEL_W - viewW, Math.max(0, player.x - viewW / 2)));
    near = ZONES.find((z) => Math.abs(z.x - player.x) < REACH) || null;
  }

  function loop(now) {
    const dt = Math.min(0.05, (now - last) / 1000 || 0);
    last = now;
    update(dt);
    draw();
    if (visible) requestAnimationFrame(loop);
  }

  // Dialog ------------------------------------------------------------------

  // say() shows lines one at a time. Options: choices [[label, fn]], done().
  function say(lines, { choices = null, done = null } = {}) {
    state = "dialog";
    keys.clear();
    dialog.hidden = false;
    talk = { lines, index: 0, choices, done, typing: null, cursor: 0 };
    showLine();
  }

  function showLine() {
    const line = talk.lines[talk.index];
    const isLast = talk.index === talk.lines.length - 1;
    srEl.textContent = line;
    choicesEl.replaceChildren();
    dialog.classList.remove("has-more");
    clearInterval(talk.typing);

    const reveal = () => {
      clearInterval(talk.typing);
      talk.typing = null;
      lineEl.textContent = line;
      if (isLast && talk.choices) showChoices();
      else dialog.classList.add("has-more");
    };

    if (reduceMotion) {
      reveal();
      return;
    }

    let i = 0;
    lineEl.textContent = "";
    talk.typing = setInterval(() => {
      i += 1;
      lineEl.textContent = line.slice(0, i);
      if (i % 3 === 0) window.sfx?.play("text");
      if (i >= line.length) reveal();
    }, 22);
    talk.reveal = reveal;
  }

  function showChoices() {
    talk.choices.forEach(([label, fn], i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "game-choice";
      btn.textContent = label;
      btn.addEventListener("click", () => {
        window.sfx?.play("select");
        close();
        fn();
      });
      btn.addEventListener("focus", () => (talk && (talk.cursor = i)));
      choicesEl.append(btn);
    });
    choicesEl.firstChild.focus();
  }

  function advance() {
    if (!talk) return;
    if (talk.typing) {
      talk.reveal();
      return;
    }
    if (talk.index < talk.lines.length - 1) {
      talk.index += 1;
      window.sfx?.play("move");
      showLine();
      return;
    }
    if (talk.choices) return;
    const done = talk.done;
    close();
    if (done) done();
  }

  function close() {
    if (talk) clearInterval(talk.typing);
    talk = null;
    dialog.hidden = true;
    choicesEl.replaceChildren();
    state = "play";
    root.focus({ preventScroll: true });
  }

  // Interactions -----------------------------------------------------------

  function interact(zone) {
    if (zone.kind === "gate") {
      window.sfx?.play("chime");
      say([
        `Now boarding: flight ${zone.flight} to ${zone.dest}.`,
        `Please proceed to gate ${zone.gate}. Have a great trip!`,
      ], { done: () => (window.cockpitLoader ? window.cockpitLoader.go(zone.href) : (location.href = zone.href)) });
      return;
    }

    say([
      "Welcome to Terminal CP, the portfolio of Cristopher Pondoc: full-stack developer, photographer and aspiring airline pilot.",
      "Gates D1, P2 and A3 are to your right. How can I help?",
    ], {
      choices: [
        ["Read about me", () => document.getElementById("about").scrollIntoView()],
        ["Show departures", () => document.getElementById("departures").scrollIntoView()],
        ["Keep exploring", () => {}],
      ],
    });
  }

  function start() {
    if (state !== "title") return;
    state = "play";
    title.hidden = true;
    root.classList.add("is-playing");
    window.sfx?.play("start");
    root.focus({ preventScroll: true });
  }

  // Input -----------------------------------------------------------------

  const MOVE = { ArrowLeft: "left", a: "left", A: "left", ArrowRight: "right", d: "right", D: "right" };
  const ACT = new Set(["ArrowUp", "Enter", " ", "w", "W"]);

  root.addEventListener("keydown", (event) => {
    if (event.target.closest(".game-choice") && (event.key === "Enter" || event.key === " ")) return;

    if (state === "title") {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        start();
      }
      return;
    }

    if (state === "dialog") {
      if (talk?.choices && !talk.typing && (event.key === "ArrowUp" || event.key === "ArrowDown")) {
        event.preventDefault();
        const buttons = [...choicesEl.children];
        const next = (talk.cursor + (event.key === "ArrowDown" ? 1 : -1) + buttons.length) % buttons.length;
        buttons[next].focus();
        return;
      }
      if (ACT.has(event.key)) {
        event.preventDefault();
        advance();
      } else if (event.key === "Escape") {
        close();
      }
      return;
    }

    if (MOVE[event.key]) {
      event.preventDefault();
      keys.add(MOVE[event.key]);
    } else if (ACT.has(event.key) && near) {
      event.preventDefault();
      interact(near);
    }
  });

  root.addEventListener("keyup", (event) => {
    if (MOVE[event.key]) keys.delete(MOVE[event.key]);
  });

  root.addEventListener("focusout", (event) => {
    if (!root.contains(event.relatedTarget)) keys.clear();
  });

  startBtn.addEventListener("click", start);

  // The title screen covers the scene, so a tap anywhere on it also starts.
  title.addEventListener("pointerdown", (event) => {
    if (event.target !== startBtn) start();
  });

  // Tap or click the scene to walk there; tapping a gate or the desk also uses it.
  canvas.addEventListener("pointerdown", (event) => {
    if (state === "title") {
      start();
      return;
    }
    if (state === "dialog") {
      advance();
      return;
    }
    const rect = canvas.getBoundingClientRect();
    const x = cam + (event.clientX - rect.left) / scale;
    const zone = ZONES.find((z) => Math.abs(z.x - x) < REACH * 1.5);
    player.target = Math.min(LEVEL_W - 16, Math.max(16, zone ? zone.x : x));
    player.after = zone || null;
  });

  dialog.addEventListener("pointerdown", (event) => {
    if (!event.target.closest(".game-choice")) advance();
  });

  // On-screen buttons for touch.
  root.querySelectorAll("[data-pad]").forEach((btn) => {
    const action = btn.dataset.pad;
    const press = (event) => {
      event.preventDefault();
      if (state === "title") return start();
      if (action === "act") {
        if (state === "dialog") advance();
        else if (near) interact(near);
        return;
      }
      keys.add(action);
    };
    const release = () => keys.delete(action);
    btn.addEventListener("pointerdown", press);
    ["pointerup", "pointerleave", "pointercancel"].forEach((type) => btn.addEventListener(type, release));
  });

  // Only run the loop while the game is on screen.
  new IntersectionObserver(([entry]) => {
    const was = visible;
    visible = entry.isIntersecting;
    if (visible && !was) {
      last = performance.now();
      requestAnimationFrame(loop);
    }
  }).observe(root);

  // Boot: load the art, swap the static fallback scene for the canvas.
  A.loadImages(["concourse-sky", "concourse-apron", "concourse-front", "player", "crowd", "flight-crew", "traffic"])
    .then((loaded) => {
      Object.assign(img, loaded);
      viewport.prepend(canvas);
      root.classList.add("is-ready");
      addEventListener("resize", resize);
      resize();
      if (reduceMotion) traffic.freeze({ cam, viewW });
      last = performance.now();
      requestAnimationFrame(loop);
    })
    .catch(() => {
      // Keep the static scene if the art fails to load.
    });

  // Small hook for automated tests.
  root.gameState = () => ({
    state, x: Math.round(player.x), cam, near: near?.gate || near?.kind || null, scale, viewW,
    planes: traffic.planes.map(A.describePlane),
    taxi: Math.round(traffic.taxi.x),
    people: crowd.people.length + flightCrew.people.length,
    crew: flightCrew.people.map((p) => Math.round(p.x)),
    line: chatter.line,
    walkers: crowd.people.filter((p) => p.v).map((p) => Math.round(p.x)),
    ...traffic.stats,
  });
})();
