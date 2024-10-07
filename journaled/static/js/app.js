document.addEventListener("DOMContentLoaded", function() {
    //blurred_entry remove on click
    document.querySelectorAll('.blurred_entry').forEach(function(el) {
        el.addEventListener('click', function() {
            el.classList.remove('blurred_entry');
        });
    });

});