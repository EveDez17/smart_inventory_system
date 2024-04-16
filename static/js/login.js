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
        return document.querySelector('[name="csrfmiddlewaretoken"]').value;
    }

    $('#login-form').submit(function(e) {
        e.preventDefault();
        const postData = {
            username: $('#username').val(),
            password: $('#password').val(),
            csrfmiddlewaretoken: getCsrfToken()  // Make sure CSRF token is included here as well
        };
        $.post(this.action, postData, function(response) {
            window.location.href = "/dashboard/";
        }).fail(function(xhr) {
            alert("Login failed: " + xhr.responseText);  // Include server response to aid debugging
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

    


