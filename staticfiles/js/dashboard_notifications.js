/* Notification AJAX*/
document.addEventListener('DOMContentLoaded', function () {
    var notifButton = document.createElement('button');
    notifButton.textContent = '10 Daily notifications';
    notifButton.classList.add('notifications-button');
    notifButton.setAttribute('id', 'notificationsButton'); // Add id attribute
    var dropdown = document.querySelector('.notifications-dropdown');

    notifButton.addEventListener('click', function (event) {
        // Prevent the default form submission if the button is of type submit
        event.preventDefault();
        
        // Toggle dropdown visibility
        if (dropdown.style.display === 'block') {
            dropdown.style.display = 'none';
        } else {
            dropdown.style.display = 'block';
        }
    });

    // Append the button to its parent element
    var notificationsContainer = document.querySelector('.notifications-container');
    notificationsContainer.appendChild(notifButton);
});








