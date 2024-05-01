// // Define the validation function for the signup form in the global scope
// function validateSignupForm(formData) {
//     // Add your validation logic here
//     // For example, check if all required fields are filled
//     if (!formData || !formData.username || !formData.email || !formData.password) {
//         alert('All fields are required for signup.');
//         return false;
//     }
//     return true;
// }

// // Define the validation function for the login form in the global scope
// function validateLoginForm(formData) {
//     // Add your validation logic here
//     // For example, check if email and password are provided
//     if (!formData || !formData.email || !formData.password) {
//         alert('Please provide both email and password for login.');
//         return false;
//     }
//     return true;
// }

// $(document).ready(function() {
//     // Form submission for signup form
//     $('#signupForm').submit(function(event) {
//         // Prevent the default form submission
//         event.preventDefault();

//         // Serialize the form data
//         var formData = $(this).serialize();

//         // Validate the signup form data
//         if (validateSignupForm(formData)) {
//             // Proceed with signup if validation passes
//             $.ajax({
//                 type: 'POST',
//                 url: '/signup',
//                 data: formData,
//                 success: function(response) {
//                     // Handle the success response from the server
//                     console.log('Signup form submitted successfully.');
//                     console.log(response);
//                     // Redirect to a new page if needed
//                     window.location.href = '/login';
//                 },
//                 error: function(xhr, status, error) {
//                     // Handle errors
//                     console.error('Error:', error);
//                 }
//             });
//         }
//     });

//     // Form submission for login form
//     $('#loginForm').submit(function(event) {
//         // Prevent the default form submission
//         event.preventDefault();

//         // Serialize the form data
//         var formData = $(this).serialize();

//         // Validate the login form data
//         if (validateLoginForm(formData)) {
//             // Proceed with login if validation passes
//             $.ajax({
//                 type: 'POST',
//                 url: '/login',
//                 data: formData,
//                 success: function(response) {
//                     // Handle the success response from the server
//                     console.log('Login form submitted successfully.');
//                     console.log(response);
//                     // Redirect to a new page if needed
//                     window.location.href = '/index';
//                 },
//                 error: function(xhr, status, error) {
//                     // Handle errors
//                     console.error('Error:', error);
//                 }
//             });
//         }
//     });
// });
