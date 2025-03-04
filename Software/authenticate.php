<?php
session_start();

// Database connection
$servername = "localhost";
$dbusername = "root"; // Default XAMPP username
$dbpassword = "";     // Default XAMPP password is empty
$dbname = "user_db";

$conn = new mysqli($servername, $dbusername, $dbpassword, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// Retrieve and sanitize user inputs
$username = $conn->real_escape_string($_POST['username']);
$password = $_POST['password'];

// Fetch user from database
$sql = "SELECT * FROM users WHERE username = '$username'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
  $user = $result->fetch_assoc();
  // Verify password
  if (password_verify($password, $user['password'])) {
    // Password is correct, start user session
    $_SESSION['username'] = $username;
    header("Location: welcome.php");
  } else {
    echo "Invalid password.";
  }
} else {
  echo "No user found with that username.";
}

$conn->close();
?>