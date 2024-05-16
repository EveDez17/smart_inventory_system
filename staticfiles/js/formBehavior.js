
document.addEventListener('DOMContentLoaded', function() {
    const hasPaperworkCheckbox = document.getElementById('has_paperwork');
    const paperworkDescriptionInput = document.querySelector('[name="paperwork_description"]');

    function togglePaperworkDescription() {
        paperworkDescriptionInput.style.display = hasPaperworkCheckbox.checked ? 'block' : 'none';
    }

    hasPaperworkCheckbox.addEventListener('change', togglePaperworkDescription);

    // Initial check in case the checkbox is pre-checked when the page loads
    togglePaperworkDescription();
});
