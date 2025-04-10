<?php
session_start();

// Database configuration
$servername = "localhost";
$dbusername = "root";
$dbpassword = "";
$dbname = "rakusens";

// Create connection
$conn = new mysqli($servername, $dbusername, $dbpassword, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// ADMIN FUNCTIONS
function isAdminLoggedIn() {
    return isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;
}

function isUserLoggedIn() {
    return isset($_SESSION['username']);
}

// Handle Admin Login
if (isset($_POST['admin_login'])) {
    $username = $conn->real_escape_string($_POST['username']);
    $password = $_POST['password'];
    
    $sql = "SELECT * FROM admins WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);
    
    if ($result->num_rows > 0) {
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['admin_username'] = $username;
    } else {
        $admin_login_error = "Invalid admin credentials";
    }
}

// Handle User Login
if (isset($_POST['user_login'])) {
    $username = $conn->real_escape_string($_POST['username']);
    $password = $_POST['password'];

    $sql = "SELECT * FROM users WHERE username = '$username'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        if (password_verify($password, $user['password'])) {
            $_SESSION['username'] = $username;
            $_SESSION['user_id'] = $user['id'];
            header("Location: welcome.php");
            exit();
        } else {
            $user_login_error = "Invalid password.";
        }
    } else {
        $user_login_error = "No user found with that username.";
    }
}

// Add new user
if (isset($_POST['add_user']) && isAdminLoggedIn()) {
    $username = $conn->real_escape_string($_POST['new_username']);
    $email = $conn->real_escape_string($_POST['new_email']);
    $password = password_hash($_POST['new_password'], PASSWORD_DEFAULT);
    
    $sql = "INSERT INTO users (username, email, password) VALUES ('$username', '$email', '$password')";
    
    if ($conn->query($sql)) {
        $add_success = "User added successfully!";
    } else {
        $add_error = "Error adding user: " . $conn->error;
    }
}

// Remove user
if (isset($_GET['delete_user']) && isAdminLoggedIn()) {
    $user_id = (int)$_GET['delete_user'];
    
    $sql = "DELETE FROM users WHERE id = $user_id";
    
    if ($conn->query($sql)) {
        $delete_success = "User deleted successfully!";
    } else {
        $delete_error = "Error deleting user: " . $conn->error;
    }
}

// Admin logout
if (isset($_GET['admin_logout'])) {
    unset($_SESSION['admin_logged_in']);
    unset($_SESSION['admin_username']);
    session_destroy();
    header("Location: index.php");
    exit();
}

// User logout
if (isset($_GET['user_logout'])) {
    unset($_SESSION['username']);
    unset($_SESSION['user_id']);
    session_destroy();
    header("Location: index.php");
    exit();
}

// Get all users for admin panel
if (isAdminLoggedIn()) {
    $users = $conn->query("SELECT id, username, email FROM users");
}
?>

