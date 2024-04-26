document.addEventListener("DOMContentLoaded", function() {
    // Add event listener to the search form
    document.getElementById("submitButton").addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        
        // Get the value from the search input field
        var searchValue = document.querySelector(".navbar-form .form-control").value;
        
        // Perform search operation (you can replace this with your desired functionality)
        if (searchValue.trim() !== "") {
            // If the search value is not empty, redirect to search results page
            window.location.href = "search-results.html?query=" + encodeURIComponent(searchValue);
        } else {
            // If the search value is empty, display an error message
            alert("Please enter a search query.");
        }
    });

    // Add event listener to explore buttons in category boxes
    var exploreButtons = document.querySelectorAll(".category-box .btn-primary");
    exploreButtons.forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent default link behavior
            
            // Get the category title
            var categoryTitle = this.parentElement.querySelector(".category-title").textContent;
            
            // Perform category-specific action (you can replace this with your desired functionality)
            alert("Exploring " + categoryTitle);
        });
    });

    // Add event listener to "Read More" buttons in top stories
    var readMoreButtons = document.querySelectorAll(".top-story .btn-primary");
    readMoreButtons.forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent default link behavior
            
            // Get the story title and URL
            var storyTitle = this.parentElement.querySelector("h3").textContent;
            var storyUrl = this.href;
            
            // Perform story-specific action (you can replace this with your desired functionality)
            alert("Reading more about: " + storyTitle + "\nURL: " + storyUrl);
        });
    });

    // Add event listener for the welcome message (if you want to trigger some action when it's clicked)
    var welcomeMessage = document.querySelector(".welcome-message");
    welcomeMessage.addEventListener("click", function(event) {
        // Perform action when the welcome message is clicked (you can replace this with your desired functionality)
        alert("Welcome to ByteSerenity!");
    });
});

