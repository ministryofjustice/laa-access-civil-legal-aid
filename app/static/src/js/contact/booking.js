async function handlePostcodeSearch() {
    const postcode = document.getElementById("postcode").value.trim();
    const addressInfo = document.getElementById("address-information-container");
    const addressSelect = document.getElementById("address_finder");
    const postcodeSearchForm = document.getElementById("postcode-search")

    if (!postcode) {
        postcodeSearchForm.querySelector(".govuk-error-message").classList.remove("govuk-visually-hidden")
        addressInfo.classList.add("govuk-!-display-none");
        return;
    }

    try {
        const response = await fetch(`/addresses/${postcode}`);
        const data = await response.json();
        const addressCount = data.length;


        if (addressCount === 0){
            postcodeSearchForm.querySelector(".govuk-error-message").classList.remove("govuk-visually-hidden")
            addressInfo.classList.add("govuk-!-display-none");
            return;
        }
        else {
            postcodeSearchForm.querySelector(".govuk-error-message").classList.add("govuk-visually-hidden")
            addressInfo.classList.remove("govuk-!-display-none");
        }

        if (postcodeSearchForm.classList.contains("govuk-form-group--error")) {
            postcodeSearchForm.classList.remove('govuk-form-group--error')
            postcodeSearchForm.removeChild(postcodeSearchForm.getElementsByClassName("govuk-error-message")[0])
        }
        addressInfo.classList.remove("govuk-!-display-none");
        addressSelect.innerHTML = '';

        const labelText = `${addressCount} address${addressCount !== 1 ? 'es' : ''} found`;

        const initialOption = document.createElement('option');
        initialOption.value = '';
        initialOption.textContent = labelText;
        addressSelect.appendChild(initialOption);

        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.formatted_address;
            option.textContent = item.formatted_address;
            addressSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error fetching addresses:", error);
    }
}

const postcode_element = document.getElementById("postcode");
if (postcode_element) {
    postcode_element.addEventListener("keypress", function(event) {
        if (event.key == "Enter" && event.target.tagName === "INPUT") {
            event.preventDefault();
            handlePostcodeSearch();
        }
    });
    document.getElementById("show-postcode").addEventListener("click", handlePostcodeSearch);
    document.getElementById("address_finder").addEventListener("change", function() {
        let selectedAddress = this.value;
        let streetAddressField = document.getElementById("street_address");
        let addressInfo = document.getElementById("address-information-container");

        addressInfo.classList.add("govuk-!-display-none");

        if (selectedAddress) {
            streetAddressField.value = selectedAddress;
        }
    });
}
