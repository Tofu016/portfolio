// Select the container for the particles
const container = document.querySelector('.container');

// Number of particles
const particleCount = 1000; // Adjust this number to control the quantity

// Create particles
for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    container.appendChild(particle);

    // Set initial random position for each particle
    const initialX = anime.random(-window.innerWidth / 2, window.innerWidth / 2);
    const initialY = anime.random(-window.innerHeight / 2, window.innerHeight / 2);

    // Animate each particle
    anime({
        targets: particle,
        translateX: [
            { value: anime.random(-window.innerWidth, window.innerWidth), duration: anime.random(4000, 6000) },
        ],
        translateY: [
            { value: anime.random(-window.innerHeight, window.innerHeight), duration: anime.random(4000, 6000) },
        ],
        scale: [0.5, 1, 0], // Particles grow and shrink continuously
        duration: anime.random(4000, 6000), // Randomize animation duration
        delay: anime.random(0, 5000), // Randomize start delay
        loop: true, // Loop the animation
        easing: 'linear', // Ensure smooth, continuous motion
        begin: () => {
            // Set the initial position of the particle
            particle.style.transform = `translate(${initialX}px, ${initialY}px)`;
        },
    });
}