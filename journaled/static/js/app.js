document.addEventListener("DOMContentLoaded", function() {
    $(document).on('click', '.blurred_entry', function(e) {
        // Remove the blurred_entry class on click
        $(this).removeClass('blurred_entry');
        
        // Stop the initial click from interacting with the children, but allow future clicks
        e.stopPropagation();
    });



    $(document).on('click', '.unblur-entry', function(e) {
        var url = $(this).attr('href');
        var entry = $(this).closest('.entry');
        var button = $(this);
    
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                entry.removeClass('blurred_entry');
                button.removeClass('unblur-entry').addClass('blur-entry');
                button.text('Blur');
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    
        e.preventDefault();
    });
    
    $(document).on('click', '.blur-entry', function(e) {
        var url = $(this).attr('href');
        var entry = $(this).closest('.entry');
        var button = $(this);
    
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                entry.addClass('blurred_entry');
                button.removeClass('blur-entry').addClass('unblur-entry');
                button.text('Unblur');
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    
        e.preventDefault();
    });
    
});