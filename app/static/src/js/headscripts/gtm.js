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
    else if (path.endsWith('/cannot-find-your-problem') || path.endsWith('/find-a-legal-adviser')) {
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
    const url = new URL(window.location.href)
    if(url.pathname.includes('/find-a-legal-adviser') && url.searchParams.has('postcode')){
        push_to_datalayer({
            event: 'mini_fala_search',
            district: window.falaData.district,
            category_name: window.falaData.category_name,
            closest_provider_mileage: window.falaData.closest_provider_mileage,
        })
    }
}

function trackPageLoadTime() {
    const labels = {
        excellent: 'Under 1 second (Excellent)',
        veryGood: '1 to 2 seconds (Very good)',
        acceptable: '2 to 3 seconds (Acceptable)',
        improve: '3 to 5 seconds (Try improving)',
        fix: 'More than 5 seconds (Needs fixing)',
    };

    function getLoadTimeInSeconds() {
        if (performance?.getEntriesByType) {
            const navEntries = performance.getEntriesByType('navigation');
            if (navEntries && navEntries.length > 0) {
                return navEntries[0].duration / 1000;
            }
        }

        // Fallback for older browsers
        if (performance?.timing) {
            const { navigationStart, loadEventEnd } = performance.timing;
            if (loadEventEnd > 0) {
                return (loadEventEnd - navigationStart) / 1000;
            }
        }

        return null;
    }

    function getLabel(seconds) {
        if (seconds < 1) return labels.excellent;
        if (seconds < 2) return labels.veryGood;
        if (seconds < 3) return labels.acceptable;
        if (seconds < 5) return labels.improve;
        return labels.fix;
    }

    const loadTime = getLoadTimeInSeconds();
    if (!loadTime || isNaN(loadTime)) return;

    const label = getLabel(loadTime);

    push_to_datalayer({
        event: 'page_load_time',
        variable_label: label,
        variable_number: loadTime.toFixed(2),
    });
}

// GTM Dom Push Events
document.addEventListener('DOMContentLoaded', function () {
    if (GTM_Loaded) {
        diagnosed();
        push_GTM_anon_id();
        mini_fala_search();
    }
});

// GTM Page Load Events
window.addEventListener('load', () => {
        trackPageLoadTime();
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
