// Chiptune sound effects, made with the Web Audio API (no audio files).
// Sound is OFF by default. The AudioContext is only created once sound is on
// and a sound is actually played, so nothing ever autoplays.

const sfx = (() => {
  const KEY = "terminal-cp-sound";
  let on = false;
  let ctx = null;

  try {
    on = localStorage.getItem(KEY) === "on";
  } catch {
    on = false;
  }

  function audio() {
    if (!ctx) ctx = new AudioContext();
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }

  function tone(freq, start, length, volume = 0.05, type = "square") {
    const ac = audio();
    const osc = ac.createOscillator();
    const gain = ac.createGain();
    const t = ac.currentTime + start;

    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    gain.gain.setValueAtTime(volume, t);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + length);
    osc.connect(gain).connect(ac.destination);
    osc.start(t);
    osc.stop(t + length);
  }

  const SOUNDS = {
    move: () => tone(880, 0, 0.04, 0.025),
    select: () => { tone(660, 0, 0.06); tone(990, 0.06, 0.08); },
    start: () => { tone(523, 0, 0.08); tone(659, 0.08, 0.08); tone(784, 0.16, 0.14); },
    text: () => tone(1200, 0, 0.02, 0.012),
    // Two-note airport announcement chime.
    chime: () => { tone(784, 0, 0.5, 0.05, "triangle"); tone(523, 0.45, 0.7, 0.05, "triangle"); },
  };

  function play(name) {
    if (!on || !SOUNDS[name]) return;
    // Browsers only allow audio after the visitor has interacted with the page.
    if (!ctx && navigator.userActivation && !navigator.userActivation.hasBeenActive) return;
    try {
      SOUNDS[name]();
    } catch {
      // Audio is a nice-to-have; never let it break the page.
    }
  }

  function render() {
    document.querySelectorAll("[data-sfx-toggle]").forEach((btn) => {
      btn.setAttribute("aria-pressed", String(on));
      btn.textContent = on ? "♪ On" : "♪ Off";
    });
  }

  function toggle() {
    on = !on;
    try {
      localStorage.setItem(KEY, on ? "on" : "off");
    } catch {
      // Private mode or blocked storage: the setting just won't persist.
    }
    render();
    play("select");
  }

  document.querySelectorAll("[data-sfx-toggle]").forEach((btn) => btn.addEventListener("click", toggle));
  render();

  // Menu blips: a tick when a link or button gets focus or hover, a confirm on click.
  let last = null;
  function blip(event) {
    const item = event.target.closest?.("a, button:not([data-sfx-toggle])");
    if (!item || item === last) return;
    last = item;
    play("move");
  }

  document.addEventListener("focusin", blip);
  document.addEventListener("mouseover", blip);
  document.addEventListener("click", (event) => {
    if (event.target.closest?.("a")) play("select");
  });

  return { play, isOn: () => on, hasContext: () => ctx !== null };
})();

window.sfx = sfx;
