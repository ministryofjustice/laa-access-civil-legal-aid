import { initAll } from 'govuk-frontend/dist/govuk/all.bundle.js';
initAll();

document.addEventListener('DOMContentLoaded', () => {
    // Find elements to control and set up their visibility toggling
    document.querySelectorAll('[data-controlled-by]').forEach(element => {
        // Get the elements we need
        const form = element.closest('.govuk-form-group');
        const radios = document.querySelector('.govuk-radios:not([data-controlled-by])')
            ?.querySelectorAll('input[type="radio"]');

        if (!form || !radios?.length) return;

        // Toggle visibility based on radio selection
        function toggle() {
            const value = element.dataset.showValue || '1';
            form.style.display = Array.from(radios)
                .some(radio => radio.checked && radio.value === value) ? 'block' : 'none';
        }

        // Run on load and when radios change
        toggle();
        radios.forEach(radio => radio.addEventListener('change', toggle));
    });
});