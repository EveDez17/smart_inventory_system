$(document).ready(function() {
    // Cancel booking and refresh list
    $('.cancel-booking').click(function(e) {
        e.preventDefault();
        var bookingId = $(this).data('id');
        if (confirm('Are you sure you want to cancel this booking?')) {
            $.ajax({
                url: '/inbound/cancel-booking/' + bookingId + '/',
                method: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    if (response.cancelled) {
                        alert('Booking cancelled successfully.');
                        updateBookingList();  // Call to refresh the booking list
                    }
                },
                error: function(xhr, status, error) {
                    alert('Error cancelling booking: ' + xhr.responseText);
                }
            });
        }
    });

    // Function to refresh the booking list
    function updateBookingList() {
        $.ajax({
            url: '/inbound/booking-list-fragment/',  // Endpoint for the booking list fragment
            method: 'GET',
            success: function(response) {
                $('#booking-list-container').html(response);  // Assuming you have a div with this ID around your table
            },
            error: function(xhr, status, error) {
                alert('Error refreshing booking list: ' + error);
            }
        });
    }
});
