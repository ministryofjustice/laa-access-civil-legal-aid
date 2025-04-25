'use strict';

//Google Tag Manager

var GTM_Loaded = false;

function add_GTM() {

    // Standard GTM code
    (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});

    // Insert our variable into data layer
    if(typeof gtm_anon_id !== 'undefined' && gtm_anon_id.length === 36) {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ user_id: gtm_anon_id });
    }

    // Continue standard GTM code
    var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';
    j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-PJPFZVSS');

    GTM_Loaded = true;
}

function push_to_datalayer(event, category_code, category_name, category_traversal, diagnosis_result) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
        event: event,
        category_code: category_code,
        category_name: category_name,
        category_traversal: category_traversal,
        diagnosis_result: diagnosis_result,
    });
}

function diagnosed(){
    const path = window.location.pathname;

    // Covers the in scope legal aid available page, the fast tracked contact
    if (path.endsWith('/legal-aid-available') || path.includes('fast-tracked')) {
        push_to_datalayer('diagnosed', window.sessionData.category_code, window.sessionData.category_name, window.sessionData.category_traversal, "INSCOPE")
    }
    // Covers the refer page
    else if (path.endsWith('/cannot-find-your-problem')) {
        push_to_datalayer('diagnosed', window.sessionData.category_code, window.sessionData.category_name, window.sessionData.category_traversal, "OUTOFSCOPE")
    }
    // Cover mini FALA search
    else if (path.includes('/find-a-legal-adviser')) {
        const searchParams = new URLSearchParams(window.location.search)
        let code = searchParams.get('category')
        let secondary = searchParams.get('secondary_category')
        if (secondary !== null) {
            code = code + ' and ' + secondary
        }
        push_to_datalayer('diagnosed',category_code=code, window.sessionData.category_name, window.sessionData.category_traversal, diagnosis_result="OUTOFSCOPE")
    }
}

// Diagnosed Events
document.addEventListener('DOMContentLoaded', function () {
    diagnosed();
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
