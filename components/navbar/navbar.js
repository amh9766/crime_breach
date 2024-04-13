// Function to load the navigation bar into the specified element
function loadNavigationBar() {
    const navbarContainer = document.getElementById('navbar-container');
    if (!navbarContainer) return;

    fetch('/components/navbar/navbar.html')
        .then(response => response.text())
        .then(data => {
            navbarContainer.innerHTML = data;
        })
        .catch(error => console.error('Error loading the navigation bar:', error));
}

// Call the function when the document content is fully loaded
document.addEventListener('DOMContentLoaded', loadNavigationBar);