function updateTimes(daySelect, timeSelect) {
    let timeSlotsData = JSON.parse(daySelect.dataset.timeSlots);
    let selectedDay = daySelect.value;

    timeSelect.innerHTML = '<option value="">Select a time:</option>';

    let times = timeSlotsData[selectedDay];

    if (times) {
        for (let time in times) {
            let option = document.createElement("option");
            option.value = times[time][0];
            option.text = times[time][1];
            timeSelect.appendChild(option);
        }
    }
};


document.addEventListener("DOMContentLoaded", function () {
    let daySelect = document.getElementById("call_another_day");
    let thirdpartydaySelect = document.getElementById("thirdparty_call_another_day")
    let timeSelect = document.getElementById("call_another_time");
    let thirdpartytimeSelect = document.getElementById("thirdparty_call_another_time");

    daySelect.addEventListener("change", function() { updateTimes(daySelect, timeSelect) });

    thirdpartydaySelect.addEventListener("change", function() { updateTimes(thirdpartydaySelect, thirdpartytimeSelect)});

});


document.getElementById("show-postcode").addEventListener("click", async function() {
    let postcode = document.getElementById("post_code").value.trim();
    let addressInfo = document.getElementById("address-information-container");
    let addressSelect = document.getElementById("address_finder");

    if (!postcode) {
        addressInfo.classList.add("govuk-!-display-none");
        return;
    }

    try {
        let response = await fetch(`/addresses/${postcode}`);
        let data = await response.json();
        let addressCount = data.length;
        const postcodeSearchForm = document.getElementById("postcode-search")

        if (addressCount === 0){
            if (!postcodeSearchForm.classList.contains("govuk-form-group--error")) {
                let error = document.createElement("p");
                error.classList.add("govuk-error-message");
                error.innerHTML = '<span class="govuk-visually-hidden">Error:</span>No addresses were found with that postcode, but you can still enter your address manually</p>'
                postcodeSearchForm.classList.add('govuk-form-group--error')
                postcodeSearchForm.insertBefore(error, document.getElementById("field-label-address-post_code"))
                addressInfo.classList.add("govuk-!-display-none");
            }
            return;
        }

        if (postcodeSearchForm.classList.contains("govuk-form-group--error")) {
            postcodeSearchForm.classList.remove('govuk-form-group--error')
            postcodeSearchForm.removeChild(postcodeSearchForm.getElementsByClassName("govuk-error-message")[0])
        }
        addressInfo.classList.remove("govuk-!-display-none");
        addressSelect.innerHTML = '';

        let labelText = `${addressCount} address${addressCount !== 1 ? 'es' : ''} found`;

        let initialOption = document.createElement('option');
        initialOption.value = '';
        initialOption.textContent = labelText;
        addressSelect.appendChild(initialOption);

        data.forEach(item => {
            let option = document.createElement('option');
            option.value = item.formatted_address;
            option.textContent = item.formatted_address;
            addressSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error fetching addresses:", error);
    }
});

document.getElementById("address_finder").addEventListener("change", function() {
    let selectedAddress = this.value;
    let streetAddressField = document.getElementById("street_address");
    let addressInfo = document.getElementById("address-information-container");

    addressInfo.classList.add("govuk-!-display-none")

    if (selectedAddress) {
        streetAddressField.value = selectedAddress;
    }
});
