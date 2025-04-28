document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector(".toggle-btn");

    // Add event listener to toggle sidebar
    toggleButton.addEventListener("click", function () {
        sidebar.classList.toggle("open"); // Toggle the 'open' class
    });
});
