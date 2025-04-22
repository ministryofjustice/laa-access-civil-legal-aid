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
      window.dataLayer.push({
        category_code: window.sessionData.category_code,
        category_name: window.sessionData.category_name,
    });
    }

    // Continue standard GTM code
    var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';
    j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-PJPFZVSS');

    GTM_Loaded = true;
}

function push_GTM_anon_id() {
    if(typeof gtm_anon_id === 'string' && gtm_anon_id.length === 36) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({ user_id: gtm_anon_id });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    if (GTM_Loaded) {
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
