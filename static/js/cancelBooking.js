// Set up CSRF token for AJAX requests
$(document).ready(function() {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {  // Good practice to include this check
                xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
            }
        }
    });
});

// Cancel booking event handler
$(document).ready(function() {
    $('.cancel-booking').click(function(e) {
        e.preventDefault();
        var bookingId = $(this).data('id');
        var cancelUrl = $(this).data('cancel-url'); // Get the URL from data attribute
        var $rowToDelete = $(this).closest('tr');

        if (confirm('Are you sure you want to cancel this booking?')) {
            $.ajax({
                url: cancelUrl, // Use the URL from the data attribute
                method: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    if (response.cancelled) {
                        $rowToDelete.fadeOut('slow', function() { 
                            $(this).remove();
                        });
                        alert('Booking cancelled successfully.');
                    } else {
                        alert('Cancellation failed. The booking was not cancelled.');
                    }
                },
                error: function(xhr, status, error) {
                    alert('Error cancelling booking: ' + error);
                }
            });
        }
    });
});



