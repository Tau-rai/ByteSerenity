function validateForm() {
      var username = document.getElementById("username").value;
      var password = document.getElementById("password").value;
      var expectedPassword = "pass2ork";

      // Check if any field is empty
      if (!username || !password) {
        alert("Please fill in all fields");
        return false;
      }
      
        // Check if email is valid
      var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Please enter a valid email address.');
        return false;
  }
      
      // Check if the entered password matches the expected password for the username
      if (username === "your_username" && password !== expectedPassword) {
        alert("Incorrect password for the username");
        return false;
      }
      
      return true;
    }
