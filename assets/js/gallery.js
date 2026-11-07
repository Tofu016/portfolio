// Lightbox for the photography page. Without JS, each photo is a plain link.
const lightbox = document.querySelector(".lightbox");
const shots = [...document.querySelectorAll("[data-gallery] .shot")];
const part = (name) => lightbox.querySelector(`[data-lb="${name}"]`);

let current = 0;

function show(index) {
  current = (index + shots.length) % shots.length;

  const shot = shots[current];
  const img = part("img");

  img.src = shot.href;
  img.alt = shot.querySelector("img").alt;
  part("title").textContent = shot.dataset.title;
  part("meta").textContent = shot.dataset.meta;
  part("count").textContent = `Frame ${current + 1} / ${shots.length}`;
}

shots.forEach((shot, index) => {
  shot.addEventListener("click", (event) => {
    event.preventDefault();
    show(index);
    lightbox.showModal();
  });
});

part("close").addEventListener("click", () => lightbox.close());
part("prev").addEventListener("click", () => show(current - 1));
part("next").addEventListener("click", () => show(current + 1));

lightbox.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") show(current - 1);
  if (event.key === "ArrowRight") show(current + 1);
});
