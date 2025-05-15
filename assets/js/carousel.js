// Plane Shots Carousel
const planeContainer = document.querySelector('#planes .tech-container');
const planeItems = document.querySelectorAll('#planes .tech-item');
let planeRotationAngle = 0;
const planeTotalItems = planeItems.length;
const planeAngle = 360 / planeTotalItems;

function updatePlaneCarousel() {
    planeItems.forEach((item, index) => {
        const itemAngle = index * planeAngle + planeRotationAngle;
        const isCenter = Math.abs((itemAngle % 360) - 0) < planeAngle / 2;

        item.style.transform = `rotateY(${itemAngle}deg) translateZ(600px)`;
        item.style.opacity = isCenter ? '1' : '0.5';
        item.style.pointerEvents = isCenter ? 'auto' : 'none';
        item.style.zIndex = isCenter ? '10' : '0';
    });
}

function rotatePlaneCarousel() {
    planeRotationAngle -= planeAngle;
    updatePlaneCarousel();
}

updatePlaneCarousel();
setInterval(rotatePlaneCarousel, 5000);

// People Shots Carousel
const peopleContainer = document.querySelector('#people .tech-container');
const peopleItems = document.querySelectorAll('#people .nature-pic');
let peopleRotationAngle = 0;
const peopleTotalItems = peopleItems.length;
const peopleAngle = 360 / peopleTotalItems;

function updatePeopleCarousel() {
    peopleItems.forEach((item, index) => {
        const itemAngle = index * peopleAngle + peopleRotationAngle;
        const isCenter = Math.abs((itemAngle % 360) - 0) < peopleAngle / 2;

        item.style.transform = `rotateY(${itemAngle}deg) translateZ(600px)`;
        item.style.opacity = isCenter ? '1' : '0.5';
        item.style.pointerEvents = isCenter ? 'auto' : 'none';
        item.style.zIndex = isCenter ? '10' : '0';
    });
}

function rotatePeopleCarousel() {
    peopleRotationAngle -= peopleAngle;
    updatePeopleCarousel();
}

updatePeopleCarousel();
setInterval(rotatePeopleCarousel, 5000);