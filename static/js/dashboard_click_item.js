/* Item Click Menu*/

document.addEventListener('DOMContentLoaded', function () {
    var sidebarMenuItems = document.querySelectorAll('.sidebar-menu-item');

    // Loop through each sidebar menu item and attach a click event listener
    sidebarMenuItems.forEach(function(menuItem) {
        menuItem.addEventListener('click', function(event) {
            // Get the URL to navigate to from the href attribute of the <a> tag inside the menu item
            var link = menuItem.querySelector('a').getAttribute('href');

            // Navigate to the new page
            window.location.href = link;
        });
    });
});
