'use strict';

//Google Tag Manager

var GTM_Loaded = false;


function element_click() {
    const element_click = (event) => {
      var clickInputTypes = ['checkbox', 'radio', 'button', 'textarea'];
      var thisIsAClickInput = clickInputTypes.includes(event.target.getAttribute('type'));

      // Don't track changes for clickable input types, only clicks
      if(event.type === 'change' && thisIsAClickInput)return;

      var elem = event.target.tagName.toLowerCase();
      var value = '';

      switch(elem) {
        case 'textarea':
        case 'input': value = thisIsAClickInput ? event.target.value : 'Redacted'; break;
        case 'button': value = event.target.innerText; break;
        case 'select': value = event.target.options[event.target.selectedIndex].text; break;
        case 'span': value = event.target.innerText; break;
      }

      value = value.trim().replace(/\n/g,'').substring(0,30); // can be up to 100 if needed
        const data = {
        'event': 'element-' + event.type,
        'element_tag': elem,
        'element_id': event.target.id,
        'element_value': value,
        'element_checked': event.target.checked  === true
      }
      console.log(data)
      window.dataLayer.push(data);

    }
    ['input', 'select', 'button', 'textarea', 'summary'].forEach((tagName) => {

        const elements = document.getElementsByTagName(tagName);
        for (const element of elements) {
            element.addEventListener("click", element_click);
            element.addEventListener("change", element_click);
        }
    });
}

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

function trackPageLoadTime() {
    const labels = {
        excellent: 'Under 1 second (Excellent)',
        veryGood: '1 to 2 seconds (Very good)',
        acceptable: '2 to 3 seconds (Acceptable)',
        improve: '3 to 5 seconds (Try improving)',
        fix: 'More than 5 seconds (Needs fixing)'
    };

    const getLoadTimeSeconds = () => {
        const navEntry = performance?.getEntriesByType?.('navigation')?.[0];
        if (!navEntry) return null;
        return navEntry.duration / 1000;
    };

    const getLabel = (time) => {
        if (time < 1) return labels.excellent;
        if (time < 2) return labels.veryGood;
        if (time < 3) return labels.acceptable;
        if (time < 5) return labels.improve;
        return labels.fix;
    };


    const loadTime = getLoadTimeSeconds();
    if (loadTime === null || isNaN(loadTime)) return;
    const label = getLabel(loadTime);
    
    push_to_datalayer({
        'event': 'page_load_time',
        'variable_label': label,
        'variable_number': parseFloat(loadTime).toFixed(2).toString()
      });

}

// GTM Dom Push Events
document.addEventListener('DOMContentLoaded', function () {
    if (GTM_Loaded) {
        console.log("GTM LOADED");
        diagnosed();
        push_GTM_anon_id();
        element_click();
    }
});

// GTM Page Load Events
window.addEventListener('load', () => {
    setTimeout(trackPageLoadTime, 1000);
});


// If user consents from banner then allow GTM to load
window.addEventListener("cookies_approved", function(event){
    if (!GTM_Loaded) {
        add_GTM();
    }
})

function getCookie(name) {
  let value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    value = parts.pop().split(';').shift();
    return value.replaceAll('\\"', '"').replaceAll('\\054', ',');
  }
  return null;
}

// If user had consented already then allow GTM to load
let cookie_policy = getCookie("cookies_policy");
if(cookie_policy) {
    cookie_policy = JSON.parse(cookie_policy.replace('"{', '{').replace('}"', '}'));
}

if (cookie_policy && cookie_policy["analytics"] == "yes" && !GTM_Loaded) {
    add_GTM();
}
