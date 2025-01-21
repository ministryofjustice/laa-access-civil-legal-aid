/**
 * Controls the visibility of form elements based on a radio button.
 * The controlled element will show when the data-controlled-by radio button value matches data-show-value.
 *
 * Usage example:
 *  {{ form.has_partner()}}
 *
 *  {{ form.partner_is_employed(params={
 *         "attributes": {
 *             "data-controlled-by": "has_partner",
 *             "data-show-value": "yes"
 *         }
 *     }) }}
 *
 *   The second question will only display when has_partner has a value of "yes" .
 *
 *   Note: This only controls whether the element should be displayed on the page, to skip the validation for this field
 *   add the ValidateIf("has_partner", "yes") validator to the start of the validation list for the field.
 */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-controlled-by]').forEach(element => {
        const form = element.closest('.govuk-form-group');
        const controllerName = element.dataset.controlledBy;
        const radios = document.querySelectorAll(`input[type="radio"][name="${controllerName}"]`);

        if (!form || !radios?.length) return;

        // Hide the element initially
        form.style.display = 'none';

        function toggle() {
            const value = element.dataset.showValue;
            form.style.display = Array.from(radios)
                .some(radio => radio.checked && radio.value === value) ? 'block' : 'none';
        }

        toggle();
        radios.forEach(radio => radio.addEventListener('change', toggle));
    });
});