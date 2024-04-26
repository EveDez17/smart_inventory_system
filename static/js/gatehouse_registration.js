$(document).ready(function() {
    $('#bookingForm').on('submit', function(e) {
      e.preventDefault(); // Stop the form from submitting normally
      var formData = $(this).serialize(); // Serialize the form data
  
      $.ajax({
        url: "{% url 'inbound:gatehouse_log' %}", // Ensure this is the correct URL for your view
        type: 'POST',
        data: formData,
        headers: {
          'X-CSRFToken': getCSRFToken() // Set the CSRF token header
        },
        success: function(response) {
          // Notify the user of success
          alert('The booking has been registered successfully');
          $('#bookingForm').trigger('reset'); // Clears the form
        },
        error: function(xhr, errmsg, err) {
          // Notify the user of an error
          alert('Please check and re-enter your details.');
        }
      });
    });
    
    // Function to get the CSRF token from the cookie
    function getCSRFToken() {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = jQuery.trim(cookies[i]);
              if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
    }
  });
  