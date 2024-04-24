$(function() {
    function getCsrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();
    }
    $(function() {
        // Set CSRF token as header for all AJAX POST requests
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
                }
            }
        });
    
        // Bind the submit event to the login form
        $('.login-form').submit(function(e) {
            e.preventDefault(); // Prevent the default form submission
    
            $.ajax({
                type: 'POST',
                url: $(this).attr('action'), // Get the action attribute from the form
                data: $(this).serialize(), // Serialize form data for submission
                dataType: 'json', // Expect a JSON response from the server
                success: function(response) {
                    console.log('AJAX response:', response);
                    if (response.success) {
                        // If successful, redirect to the URL provided by the server
                        window.location.href = response.redirect_url;
                    } else {
                        // If not successful, display the error message from the server
                        $("#login-error").text(response.error).show();
                    }
                },
                error: function(xhr, status, error) {
                    if (xhr.responseText.startsWith('<!DOCTYPE html>')) {
                        console.error('HTML response received, possibly due to a server error.');
                    } else {
                        console.error("Error response:", xhr.responseText);
                    }
                }
                
            });
        });
    });
    

    function getCookie(name) {
        let cookie = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const part = cookies[i].trim();
                if (part.substring(0, name.length + 1) === (name + '=')) {
                    cookie = decodeURIComponent(part.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookie;
    }
});
