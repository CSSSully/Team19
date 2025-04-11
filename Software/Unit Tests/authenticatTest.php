<?php
session_start();

// Database connection function
function getDatabaseConnection() {
    $servername = "localhost";
    $dbusername = "root"; // Default XAMPP username
    $dbpassword = "";     // Default XAMPP password is empty
    $dbname = "user_db";

    $conn = new mysqli($servername, $dbusername, $dbpassword, $dbname);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    return $conn;
}

// Function to get user data from the database based on username
function getUserFromDatabase($conn, $username) {
    $username = $conn->real_escape_string($username);
    $sql = "SELECT * FROM users WHERE username = '$username'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        return $result->fetch_assoc();
    } else {
        return null;
    }
}

// Function to verify the user's password
function verifyPassword($inputPassword, $storedPassword) {
    return password_verify($inputPassword, $storedPassword);
}

// Test the login process
function login($username, $password) {
    $conn = getDatabaseConnection();
    $user = getUserFromDatabase($conn, $username);

    if ($user && verifyPassword($password, $user['password'])) {
        $_SESSION['username'] = $username;
        $conn->close();
        return true;
    } else {
        $conn->close();
        return false;
    }
}

// Test function to assert equality
function assertEquals($input, $expectedOutput) {
    if($input == $expectedOutput) {
        echo 'SUCCESS';
        return TRUE;
    } else {
        echo 'FAILED';
        return FALSE;
    }
}

// Test function to assert true
function assertTrue($input) {
    if($input == TRUE ) {
        echo 'SUCCESS';
        return TRUE;
    } else {
        echo 'FAILED';
        return FALSE;
    }
}

?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Test Login System</title>
    </head>
    <body>
        <h1>Test Login Function</h1>
        <?php
        // Example to test login with valid username and password
        echo assertTrue(login('validUsername', 'validPassword')); // Replace with actual test data

        // Example to test login with invalid username
        echo assertTrue(!login('invalidUsername', 'password')); 

        // Example to test login with invalid password
        echo assertTrue(!login('validUsername', 'invalidPassword'));
        ?>
    </body>
</html>
