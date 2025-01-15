import { initAll } from 'govuk-frontend/dist/govuk/all.bundle.js';
initAll();

document.addEventListener('DOMContentLoaded', function() {
    const dependentElements = document.querySelectorAll('[data-depends-on]');

    function updateVisibility() {
        dependentElements.forEach(element => {
            // Check parent condition first
            const parentField = element.dataset.parentField;
            const parentValue = element.dataset.parentValue;
            const parentSelected = document.querySelector(
                `input[name="${parentField}"]:checked`
            )?.value === parentValue;

            // Only check the dependent field if parent condition is met
            const controllingField = element.dataset.dependsOn;
            const requiredValue = element.dataset.dependsOnValue;
            const dependentSelected = document.querySelector(
                `input[name="${controllingField}"]:checked`
            )?.value === requiredValue;

            // Show only if both conditions are met
            const shouldShow = parentSelected && dependentSelected;
            element.classList.toggle('govuk-radios__conditional--hidden', !shouldShow);
        });
    }

    // Listen for changes on any radio button
    document.addEventListener('change', function(event) {
        if (event.target.type === 'radio') {
            requestAnimationFrame(updateVisibility);
        }
    });

    // Initial state
    updateVisibility();
});
