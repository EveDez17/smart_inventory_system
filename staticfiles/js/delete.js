
document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(e) {
        if (e.target.matches('.delete-btn')) {
            var productId = e.target.dataset.productId;
            var confirmDeleteButton = document.getElementById('confirm-delete');
            if (confirmDeleteButton) {
                confirmDeleteButton.dataset.productId = productId;
            }
        }
    });

    var confirmDeleteButton = document.getElementById('confirm-delete');
    if (confirmDeleteButton) {
        confirmDeleteButton.addEventListener('click', function() {
            var productId = this.dataset.productId;
            var deleteUrl = deleteUrlTemplate.replace('__pk__', productId);

            // Create and submit a form for deletion
            var form = document.createElement('form');
            form.method = 'post';
            form.action = deleteUrl;

            // CSRF token is required for POST requests
            var csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);

            document.body.appendChild(form);
            form.submit();
        });
    }
});

