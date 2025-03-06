/* Replaces the current page in the history with a GET request to the current page.
* This prevents the "Confirm form resubmission" page from showing, as the browser will never attempt to resubmit the form when the back button is pressed.
*/

if ( window.history.replaceState ) {  // Only do this if the browser supports history.replaceState
    window.history.replaceState( null, null, window.location.href );
}
