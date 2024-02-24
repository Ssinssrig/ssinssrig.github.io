// Listens for the event once page is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    jQuery.noConflict();

    // Collapses all cards except of activated one
    jQuery(document).ready(function($) {
        jQuery('.collapse').on('show.bs.collapse', function() {
            jQuery('.collapse.show').not(jQuery(this)).collapse('hide');
        });
    });

    // Erasing blinking "CLICK HERE" from the button
    let clickHere = document.querySelectorAll('.clickbutton');
    clickHere.forEach(button => {
        button.addEventListener('click', () => {
            document.getElementById('clickhere').innerHTML = "";
        })
    });
});
