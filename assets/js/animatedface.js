document.addEventListener("DOMContentLoaded", function () {
    const imageElement = document.getElementById("animated-image");
    const images = [
        "imgassets/portfolio/face/face-1.jpg",
        "imgassets/portfolio/face/face-2.jpg",
        "imgassets/portfolio/face/face-3.jpg",
        "imgassets/portfolio/face/face-4.jpg"
    ];
    let currentIndex = 0;

    function switchImage() {
        imageElement.style.opacity = 0;

        setTimeout(() => {
            currentIndex = (currentIndex + 1) % images.length;
            imageElement.src = images[currentIndex];

            imageElement.style.opacity = 1;
        }, 1000);
    }

    setInterval(switchImage, 3000);
});
