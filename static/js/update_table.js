document.addEventListener("DOMContentLoaded", function() {
    // Scroll the page to the bottom of the form
    document.getElementById('your-form').scrollIntoView({ behavior: 'smooth', block: 'end' });

    // Function to update the table after form submission
    function updateTable() {
        // Make an AJAX request to fetch the updated product data
        // Replace '/fetch_updated_products/' with the appropriate URL endpoint
        fetch('/fetch_updated_products/')
            .then(response => response.json())
            .then(data => {
                // Update the table body with the new product data
                const tableBody = document.querySelector('#product-table tbody');
                tableBody.innerHTML = ''; // Clear existing table rows
                data.forEach(product => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${product.sku}</td>
                        <td>${product.name}</td>
                        <td>${product.description}</td>
                        <td>${product.quantity}</td>
                        <td>${product.unit_price}</td>
                        <td>${product.batch_number}</td>
                        <td>${product.expiration_date}</td>
                        <td>${product.storage_temperature}</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching updated products:', error));
    }

    // Add event listener to the form submission
    document.getElementById('your-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        // Submit the form data using AJAX
        fetch(this.action, {
            method: this.method,
            body: new FormData(this),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
            }
        })
        .then(response => {
            if (response.ok) {
                // If form submission is successful, update the table
                updateTable();
            } else {
                throw new Error('Form submission failed');
            }
        })
        .catch(error => console.error('Error submitting form:', error));
    });
});
