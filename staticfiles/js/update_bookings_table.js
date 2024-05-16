// JavaScript code to update the table using AJAX
function updateBookingsTable() {
    $.ajax({
        url: '/api/Not working',  // Correct URL endpoint
        success: function(data) {
            // Clear existing table rows
            $('#bookings-table tbody').empty();

            // Populate table rows with fetched data
            data.bookings.forEach(function(booking) {
                var newRow = $('<tr>');
                newRow.append($('<td>').text(booking.driver_name));
                newRow.append($('<td>').text(booking.company));
                newRow.append($('<td>').text(booking.vehicle_registration));
                newRow.append($('<td>').text(booking.trailer_number));
                newRow.append($('<td>').text(booking.arrival_time));
                newRow.append($('<td>').text(booking.has_paperwork));
                newRow.append($('<td>').text(booking.paperwork_description));
                newRow.append($('<td>').text(booking.cancelled));
                $('#bookings-table tbody').append(newRow);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error fetching bookings:', error);
        }
    });
}

// Initial call to populate the table
updateBookingsTable();

// Periodically update the table
setInterval(updateBookingsTable, 5000);


