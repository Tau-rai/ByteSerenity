$(document).ready(function() {
    // // Toggle the dropdown menu for small screens
    // var menuToggle = document.getElementById("menu-toggle");
    // var dropdownMenu = document.getElementById("dropdown-menu");

    // menuToggle.addEventListener("click", function() {
    //     dropdownMenu.classList.toggle("hidden");
    // });


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
});
