const planeBtn = document.getElementById('plane-btn');
const peopleBtn = document.getElementById('people-btn');
const planesSection = document.getElementById('planes');
const peopleSection = document.getElementById('people');
const buttonContainer = document.querySelector('.button-container');

function toggleSection(sectionToShow, sectionToHide) {
    // Hide the currently visible section
    if (sectionToHide) {
        sectionToHide.classList.remove('active');
        sectionToHide.classList.add('hidden');
    }

    // Show the selected section
    sectionToShow.classList.remove('hidden');
    sectionToShow.classList.add('active');

    // Move buttons to the top
    buttonContainer.classList.add('active');
}

// Event listeners for buttons
planeBtn.addEventListener('click', () => {
    toggleSection(planesSection, peopleSection);
});

peopleBtn.addEventListener('click', () => {
    toggleSection(peopleSection, planesSection);
});