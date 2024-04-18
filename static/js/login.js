$(function() {
    // Set CSRF token as header for all AJAX POST requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
            }
        }
    });

    function getCsrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();  // Simplified CSRF token retrieval
    }

    // Login form submission event handler
    $('#login-form').submit(function(e) {
        e.preventDefault();
        
        const postData = {
            username: $('#username').val().trim(),  // Trim inputs to remove accidental whitespace
            password: $('#password').val().trim(),
            csrfmiddlewaretoken: getCsrfToken()  // Ensure CSRF token is included
        };

        $.post(this.action, postData, function(response) {
            // Assume response contains a JSON object with a 'redirect' field
            if (response.redirect) {
                window.location.href = response.redirect;  // Use redirect URL provided by the server
            } else {
                alert('Login successful - redirect path missing in response.');
            }
        }).fail(function(xhr) {
            var errorMsg = "Login failed: " + (xhr.responseJSON ? xhr.responseJSON.message : xhr.responseText);
            alert(errorMsg);  // Enhanced error handling
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

    


