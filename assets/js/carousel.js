const techContainer = document.querySelector('.tech-container');
const techItems = document.querySelectorAll('.tech-item');
let rotationAngle = 0; // Cumulative rotation angle
const totalItems = techItems.length; // Get the total number of items
const angle = 360 / totalItems; // Calculate the angle for each item

function updateCarousel() {
    techItems.forEach((item, index) => {
        const itemAngle = index * angle + rotationAngle; // Calculate the angle for each item
        const isCenter = Math.abs((itemAngle % 360) - 0) < angle / 2; // Check if the item is at the center

        // Apply transformations
        item.style.transform = `rotateY(${itemAngle}deg) translateZ(600px)`;
        item.style.opacity = isCenter ? '1' : '0.5'; // Only the center item is visible
        item.style.pointerEvents = isCenter ? 'auto' : 'none'; // Disable interaction for non-center items
        item.style.zIndex = isCenter ? '10' : '0'; // Bring the center item to the front
    });
}

function rotateCarousel() {
    rotationAngle -= angle; // Increment the rotation angle
    updateCarousel();
}

// Initialize carousel
updateCarousel();

// Rotate carousel continuously every 2 seconds
setInterval(rotateCarousel, 3000);