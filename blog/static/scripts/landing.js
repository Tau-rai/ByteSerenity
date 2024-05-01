// Get all the explore buttons
var exploreButtons = document.querySelectorAll('.category-box .btn-primary');

// Add click event listener to each explore button
exploreButtons.forEach(function(button) {
    button.addEventListener('click', function(event) {
        // Prevent default behavior of the anchor tag
        event.preventDefault();
        
        // Get the URL from the href attribute of the anchor tag
        var url = this.getAttribute('href');
        
        // Open the URL in a new tab
        window.open(url, '_blank');
    });
});

// Get all the "Read More" buttons
var readMoreButtons = document.querySelectorAll('.top-story .btn.btn-primary');

// Add click event listener to each "Read More" button
readMoreButtons.forEach(function(button) {
    button.addEventListener('click', function(event) {
        // Prevent default behavior of the anchor tag
        event.preventDefault();
        
        // Get the URL from the href attribute of the anchor tag
        var url = this.getAttribute('href');
        
        // Open the URL in a new tab
        window.open(url, '_blank');
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Your JavaScript code here
    var searchForm = document.querySelector('.navbar-form');
    // Add event listener to the search form
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        var searchInput = this.querySelector('input').value;
        console.log('Searching for:', searchInput);
    });
});


