$(function() {
    function getCsrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val();
    }

    // Set CSRF token as header for all AJAX POST requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
            }
        }
    });

    $('.login-form').submit(function(e) {
        e.preventDefault();
        const postData = {
            username: $('#username').val().trim(),
            password: $('#password').val().trim(),
            csrfmiddlewaretoken: getCsrfToken()
        };

        $.ajax({
            type: 'POST',
            url: this.action,
            data: postData,
            dataType: 'json',
            success: function(response) {
                if (response.redirect) {
                    window.location.href = response.redirect;
                } else {
                    $("#login-error").text('Login successful - redirect path missing in response.').show();
                }
            },
            error: function(xhr) {
                const errorMsg = "Login failed: " + (xhr.responseJSON ? xhr.responseJSON.message : xhr.statusText);
                $("#login-error").text(errorMsg).show();
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

    


