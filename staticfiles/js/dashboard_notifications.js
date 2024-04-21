
$document.addEventListener('DOMContentLoaded', function () {
    var notifButton = document.querySelector('.notifications-button');
    var dropdown = document.querySelector('.notifications-dropdown');

    notifButton.onclick = function () {
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    };
});


/* Fetch Icons dynamically*/

fetch('{% static "images/icins/machine-vision-svgrepo-com.svg" %}')
    .then(response => response.text())
    .then(data => {
        document.querySelector('.icon-placeholder').innerHTML = data;
    })
    .catch(error => console.error('Error loading the SVG:', error));

