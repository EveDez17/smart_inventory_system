// Gatehouse Log handle

document.addEventListener('DOMContentLoaded', function() {
    fetchAndRenderAssignments();
});

async function fetchAndRenderAssignments() {
    try {
        const response = await fetch('/inbound/provisional-bay-assignments/');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const assignments = await response.json();
        renderAssignments(assignments);
    } catch (error) {
        console.error('Error fetching the data:', error);
        // Optionally handle the error visually in the UI
    }
}

function renderAssignments(assignments) {
    const tableBody = document.querySelector('.table-style tbody');
    if (!tableBody) {
        console.error('Table body element not found');
        return;
    }
    tableBody.innerHTML = ''; // Clear current table body
    assignments.forEach(assignment => {
        const row = tableBody.insertRow();
        row.innerHTML = `
            <td>${assignment.provisional_bay}</td>
            <td>${assignment.assigned_by}</td>
            <td>${assignment.assigned_at}</td>
            <td>${assignment.gatehouse_booking.driver_name}</td> <!-- Make sure this matches your data structure -->
        `;
    });
}




