$(document).ready(function() {
    // Toggle the dropdown menu for small screens
    var menuToggle = document.getElementById("menu-toggle");
    var dropdownMenu = document.getElementById("dropdown-menu");

    menuToggle.addEventListener("click", function() {
        dropdownMenu.classList.toggle("hidden");
    });

    // Handle the Create Post form submission
    $('#create-post-form').submit(function(event) {
        event.preventDefault();
        var title = $('#title').val().trim();
        var body = $('#body').val().trim();
        var tags = $('#tags').val().trim();
        var action = $('input[type="submit"][clicked=true]').val();

        if (title === '' || body === '') {
            alert('Please fill out both the title and body fields.');
            return;
        }

        $.ajax({
            url: '/create',
            type: 'POST',
            data: { title: title, body: body, tags: tags, action: action },
            dataType: 'json',
            success: function(response) {
                // Redirect to the index page or display a success message
                window.location.href = '/';
            },
            error: function(xhr, status, error) {
                // Handle errors (e.g., display error messages)
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.message : 'An error occurred. Please try again later.';
                alert(errorMessage);
            }
        });
    });

    // Capture the clicked submit button
    $(document).on('click', 'form input[type="submit"]', function() {
        $('input[type="submit"]', $(this).parents('form')).removeAttr('clicked');
        $(this).attr('clicked', 'true');
    });

    // Handle the Add Comment form submission
    $('.comment-form').submit(function(event) {
        event.preventDefault();
        var postId = $(this).data('post-id');
        var body = $(this).find('.comment-body').val();

        // Perform validation if needed

        $.ajax({
            url: '/'+ postId +'/comment',
            type: 'POST',
            data: { body: body },
            success: function(response) {
                // Reload the page to show the new comment
                location.reload();
            },
            error: function(error) {
                // Handle errors
                console.error('Error adding comment:', error);
            }
        });
    });

   // Handle the Search functionality
    $('#search-form').submit(function(event) {
        event.preventDefault();
        var query = $('#search-query').val().trim(); // Trim leading and trailing whitespace

        // Check if the search input is empty
        if (query === '') {
            alert('Please enter a topic or title to search.');
        } else {
            // Redirect to the search results page
            window.location.href = '/search?q=' + encodeURIComponent(query);
        }
    });

    // Handle like button click
    $("#like-button").click(function() {
        $.ajax({
            url: '/like_post/{{ post.id }}',
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                console.log(data);
                $("#like-count").text(data['like_count']);
            }
        });
    });

    // Handle the Delete Post functionality
    $('.delete-post-button').click(function() {
        var postId = $(this).data('post-id');
        var confirmation = confirm('Are you sure you want to delete this post?');

        if (!confirmation) {
            return;
        }

        $.ajax({
            url: '/' + postId + '/delete',
            type: 'POST',
            dataType: 'json',
            success: function(response) {
                // Redirect to the index page or display a success message
                window.location.href = '/';
            },
            error: function(xhr, status, error) {
                // Handle errors
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.message : 'An error occurred. Please try again later.';
                alert(errorMessage);
            }
        });
    });

    // // Handle profile form submission with jQuery AJAX
    // $('#profile-form').submit(function(event) {
    //     event.preventDefault();
    
    //     var firstName = $('#first_name').val().trim();
    //     var lastName = $('#last_name').val().trim();
    //     var dateOfBirth = $('#date_of_birth').val().trim();
    //     var bio = $('#bio').val().trim();
    //     var email = $('#email').val().trim();
    //     var profilePicture = $('#profile_picture').prop('files')[0]; // Get the uploaded file
    
    //     // Validate email address
    //     var emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/;
    //     if (!emailRegex.test(email)) {
    //         alert('Please enter a valid email address.');
    //         return;
    //     }
    
    //     // Prepare data for AJAX request
    //     var formData = new FormData(); // Use FormData to handle file upload
    //     formData.append('first_name', firstName);
    //     formData.append('last_name', lastName);
    //     formData.append('date_of_birth', dateOfBirth);
    //     formData.append('bio', bio);
    //     formData.append('email', email);
    
    //     // Append the file to formData only if profilePicture is not undefined
    //     if (profilePicture) {
    //         formData.append('profile_picture', profilePicture);
    //     }
    
    //     // Send AJAX request to update profile
    //     $.ajax({
    //         url: '/profile',
    //         type: 'POST',
    //         processData: false,  // Important for file upload
    //         contentType: false,  // Important for file upload
    //         data: formData,
    //         success: function(response) {
    //             // Handle successful response
    //             alert('Profile updated successfully.');
    //         },
    //         error: function(xhr, status, error) {
    //             // Handle error
    //             alert('An error occurred while updating the profile.');
    //         }
    //     });
    // });
    
    // // Script for toggling the edit profile form
    // $("#edit-profile-btn").click(function() {
    //     $("#edit-profile-form").toggleClass("hidden");
    // });   

});
