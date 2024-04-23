$(document).ready(function() {
    // Setup the CSRF token for AJAX post requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^https?:.*/.test(settings.url) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
            }
        }
    });

    // Handle click event on delete buttons
    $('.delete-booking').click(function(e) {
        e.preventDefault();
        var bookingId = $(this).data('id'); // Make sure 'data-id' attribute is set in your HTML

        if (confirm('Are you sure you want to delete this booking?')) {
            $.ajax({
                url: '/path/to/delete/booking/', // Update with the path to your delete view
                method: 'POST', // Use 'method' instead of 'type'
                data: {
                    'booking_id': bookingId,
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    // Check for a property in your response indicating the booking was deleted
                    if (response.deleted) {
                        // Remove the table row with a fade out animation
                        $('#booking-' + bookingId).fadeOut('slow', function() {
                            $(this).remove();
                        });
                        alert('Booking deleted successfully.');
                    } else {
                        // Handle failure (e.g., if 'deleted' is false or not present)
                        alert('Could not delete the booking.');
                    }
                },
                error: function(xhr, status, error) {
                    // Provide more detailed information about the error
                    alert('Something went wrong: ' + status + ', ' + error);
                }
            });
        }
    });
});

