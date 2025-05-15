document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleButton = document.querySelector(".toggle-btn");

    toggleButton.addEventListener("click", function () {
        sidebar.classList.toggle("open");
    });
});
