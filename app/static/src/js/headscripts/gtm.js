'use strict';

//Google Tag Manager

var GTM_Loaded = false;

function add_GTM() {

    // Standard GTM code
    (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});

    // Continue standard GTM code
    var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';
    j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-PJPFZVSS');

    GTM_Loaded = true;
}

function push_to_datalayer(params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ ...params });
}

function push_GTM_anon_id() {
    if(typeof gtm_anon_id === 'string' && gtm_anon_id.length === 36) {
        push_to_datalayer({ user_id: gtm_anon_id });
    }
}

function diagnosed(){
    const path = window.location.pathname;
    const categoryData = {
        event: 'diagnosed',
        category_code: window.sessionData.category_code,
        category_name: window.sessionData.category_name,
        category_traversal: window.sessionData.category_traversal,
    };

    let diagnosis_result = null;

    // Covers the in scope legal aid available page, the fast tracked contact
    if (path.endsWith('/legal-aid-available') || path.includes('fast-tracked')) {
        diagnosis_result = "INSCOPE";
    }
    // Covers the refer page and FALA search
    else if (path.endsWith('/cannot-find-your-problem') || path.includes('/find-a-legal-adviser')) {
        diagnosis_result = "OUTOFSCOPE";
    }

    if (diagnosis_result !== null) {
        push_to_datalayer({
            ...categoryData,
            diagnosis_result
        });
    }
}

function mini_fala_search(){

    const falaData = {
        'event': 'fala_search',
        'district': window.falaData.district,
        'category_name': window.falaData.category_name,
        'closest_provider_mileage': window.falaData.closest_provider_mileage,
    }

    if(window.location.pathname.includes('/find-a-legal-adviser')){
        push_to_datalayer({ falaData })
    }
}

// GTM Dom Push Events
document.addEventListener('DOMContentLoaded', function () {
    if (GTM_Loaded) {
        diagnosed();
        push_GTM_anon_id();
    }
});


// If user consents from banner then allow GTM to load
window.addEventListener("cookies_approved", function(event){
    if (!GTM_Loaded) {
        add_GTM();
    }
})

// If user had consented already then allow GTM to load
if (document.cookie && document.cookie.indexOf('cookies_policy={"analytics": "yes", "functional": "yes"}') > -1 && !GTM_Loaded) {
    add_GTM();
}
