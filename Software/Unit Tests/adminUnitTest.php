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
function handleAdminLogin() {
    global $conn;
    if (isset($_POST['admin_login'])) {
        $username = $conn->real_escape_string($_POST['username']);
        $password = $_POST['password'];
        
        $sql = "SELECT * FROM admins WHERE username = '$username'";
        $result = $conn->query($sql);
        
        if ($result->num_rows > 0) {
            $admin = $result->fetch_assoc();
            if (password_verify($password, $admin['password'])) {
                $_SESSION['admin_logged_in'] = true;
                $_SESSION['admin_username'] = $username;
                return "Admin logged in successfully!";
            } else {
                return "Invalid admin password";
            }
        } else {
            return "No admin found with that username";
        }
    }
}

// Handle User Login
function handleUserLogin() {
    global $conn;
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
                return "User logged in successfully!";
            } else {
                return "Invalid password.";
            }
        } else {
            return "No user found with that username.";
        }
    }
}

// Add new user
function handleAddUser() {
    global $conn;
    if (isset($_POST['add_user']) && isAdminLoggedIn()) {
        $username = $conn->real_escape_string($_POST['new_username']);
        $email = $conn->real_escape_string($_POST['new_email']);
        $password = password_hash($_POST['new_password'], PASSWORD_DEFAULT);
        
        $sql = "INSERT INTO users (username, email, password) VALUES ('$username', '$email', '$password')";
        
        if ($conn->query($sql)) {
            return "User added successfully!";
        } else {
            return "Error adding user: " . $conn->error;
        }
    }
}

// Remove user
function handleDeleteUser() {
    global $conn;
    if (isset($_GET['delete_user']) && isAdminLoggedIn()) {
        $user_id = (int)$_GET['delete_user'];
        
        $sql = "DELETE FROM users WHERE id = $user_id";
        
        if ($conn->query($sql)) {
            return "User deleted successfully!";
        } else {
            return "Error deleting user: " . $conn->error;
        }
    }
}

// Assert functions for testing
function assertEquals($input, $expectedOutput) {
    if ($input == $expectedOutput) {
        echo 'SUCCESS<br>';
        return TRUE;
    } else {
        echo 'FAILED<br>';
        return FALSE;
    }
}

function assertTrue($input) {
    if ($input == TRUE) {
        echo 'SUCCESS<br>';
        return TRUE;
    } else {
        echo 'FAILED<br>';
        return FALSE;
    }
}

// Test database connection
function testDatabaseConnection() {
    global $conn;
    assertTrue($conn->connect_error === null);
}

// Test admin login functionality
function testAdminLogin() {
    // Simulate POST data for admin login
    $_POST['admin_login'] = true;
    $_POST['username'] = 'admin';  // Replace with a valid admin username
    $_POST['password'] = 'password';  // Replace with a valid admin password

    // Simulate the admin login action
    $result = handleAdminLogin();
    
    assertEquals('Admin logged in successfully!', $result);
}

// Test user login functionality
function testUserLogin() {
    // Simulate POST data for user login
    $_POST['user_login'] = true;
    $_POST['username'] = 'testuser';  // Replace with a valid test user username
    $_POST['password'] = 'testpassword';  // Replace with a valid test user password

    // Simulate the user login action
    $result = handleUserLogin();
    
    assertEquals('User logged in successfully!', $result);
}

// Test adding a new user
function testAddUser() {
    $_POST['add_user'] = true;
    $_POST['new_username'] = 'new_user';
    $_POST['new_email'] = 'newuser@example.com';
    $_POST['new_password'] = 'newpassword123';

    // Simulate adding a new user
    $result = handleAddUser();
    
    assertEquals('User added successfully!', $result);
}

// Test deleting a user
function testDeleteUser() {
    $_GET['delete_user'] = 1;  // Replace with a valid user ID for deletion

    // Simulate deleting a user
    $result = handleDeleteUser();
    
    assertEquals('User deleted successfully!', $result);
}

// Test all functions
echo '<h1>Test Database Connection</h1>';
testDatabaseConnection();

echo '<h1>Test Admin Login</h1>';
testAdminLogin();

echo '<h1>Test User Login</h1>';
testUserLogin();

echo '<h1>Test Add User</h1>';
testAddUser();

echo '<h1>Test Delete User</h1>';
testDeleteUser();
?>

