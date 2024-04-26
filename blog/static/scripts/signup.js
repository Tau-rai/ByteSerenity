function validateForm() {
  // Get values from the form
  var username = document.getElementById('Username').value;
  var email = document.getElementById('email').value;
  var password = document.getElementById('password').value;
  var confirmPassword = document.getElementById('confirmPassword').value;
  var terms = document.getElementById('terms').checked;

  // Check if any field is empty
  if (!username || !email || !password || !confirmPassword) {
    alert('All fields are required.');
    return false;
  }

  // Check if email is valid
  var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert('Please enter a valid email address.');
    return false;
  }

  // Check if password is at least 8 characters long
  if (password.length < 8) {
    alert('Password must be at least 8 characters long.');
    return false;
  }

  // Check if password and confirm password match
  if (password !== confirmPassword) {
    alert('Passwords do not match.');
    return false;
  }

  // Check if terms and conditions are accepted
  if (!terms) {
    alert('You must agree to the terms and conditions.');
    return false;
  }

  // If all checks pass, allow the form to be submitted
  return true;
}

