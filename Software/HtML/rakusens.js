// Get the checkbox element
const checkbox = document.getElementById('checkbox');

// Add an event listener to the checkbox
checkbox.addEventListener('change', function () {
    // Toggle the 'dark-mode' class on the body element
    document.body.classList.toggle('dark-mode', this.checked);
});
