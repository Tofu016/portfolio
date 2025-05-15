const container = document.querySelector('.container');

const particleCount = 1000;

for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    container.appendChild(particle);

    const initialX = anime.random(-window.innerWidth / 2, window.innerWidth / 2);
    const initialY = anime.random(-window.innerHeight / 2, window.innerHeight / 2);


    anime({
        targets: particle,
        translateX: [
            { value: anime.random(-window.innerWidth, window.innerWidth), duration: anime.random(4000, 6000) },
        ],
        translateY: [
            { value: anime.random(-window.innerHeight, window.innerHeight), duration: anime.random(4000, 6000) },
        ],
        scale: [0.5, 1, 0],
        duration: anime.random(4000, 6000),
        delay: anime.random(0, 5000),
        loop: true,
        easing: 'linear',
        begin: () => {
            particle.style.transform = `translate(${initialX}px, ${initialY}px)`;
        },
    });
}