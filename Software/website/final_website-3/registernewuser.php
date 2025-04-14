<?php
// Connect to the DB
$servername = "localhost";
$username = "root";
$password = ""; 
$database = "rakusens";

$conn = new mysqli($servername, $username, $password, $database);

// Check DB connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
// connect to the database


$errors = array();


// REGISTER USER
if (isset($_POST['Signup'])) {
  // receive all input values from the form
 
  $username = mysqli_real_escape_string($db, $_POST['username']);
  $email = mysqli_real_escape_string($db, $_POST['emailaddress']);
  $password_1 = mysqli_real_escape_string($db, $_POST['password']);
  $password_2 = mysqli_real_escape_string($db, $_POST['repassword']);


  // form validation: ensure that the form is correctly filled ...
  // by adding (array_push()) corresponding error unto $errors array
 
 if (empty($username)) { array_push($errors, "Username is required"); }
  if (empty($email)) { array_push($errors, "Email is required"); }
  if (empty($password_1)) { array_push($errors, "Password is required"); }
  if ($password_1 != $password_2) {
  array_push($errors, "The two passwords do not match");
  }


  // first check the database to make sure
  // a user does not already exist with the same username and/or email
 
  $user_check_query = "SELECT * FROM users WHERE username='$username' OR email='$email' LIMIT 1";
  $result = mysqli_query($db, $user_check_query);
  $user = mysqli_fetch_assoc($result);
 
  if ($user) { // if user exists
    if ($user['username'] === $username) {
      array_push($errors, "Username already exists");
    }


    if ($user['email'] === $email) {
      array_push($errors, "email already exists");
    }
  }


  // Finally, register user if there are no errors in the form
  if (count($errors) == 0) {
    $password = md5($password_1);//encrypt the password before saving in the database


    $query = "INSERT INTO users (username, password, email,role)
          VALUES('$username', '$password','$email','0')";
    mysqli_query($db, $query);
   
    header('location: ../html/login.html');
  }
}

