document.addEventListener('DOMContentLoaded', function() {
    const avatar = document.querySelector('.avatar');
    const badge = avatar.querySelector('.badge');

    // Function to simulate fetching user status
    function updateUserStatus() {
        // This is where you'd have logic to get the user's status.
        // For demonstration, we'll cycle through statuses every 4 seconds.
        const statuses = ['active', 'inactive', 'idle', 'do_not_disturb'];
        let index = 0;

        setInterval(() => {
            // Remove all status classes
            avatar.classList.remove('active', 'inactive', 'idle', 'do_not_disturb');
            // Add the new status class
            avatar.classList.add(statuses[index]);
            // Cycle to the next status
            index = (index + 1) % statuses.length;
        }, 4000);
    }

    updateUserStatus();
});
