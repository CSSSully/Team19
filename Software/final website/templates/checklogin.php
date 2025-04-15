<?php
// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

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

// Get input
$loginid=$_POST['username'];
$password=$_POST['password'];


$password=md5($password);


$user_check_query="SELECT * FROM users WHERE username ='$loginid' AND  password = '$password'";

/*$result = $mysqli->query("SELECT * FROM users WHERE username ='$loginid' AND  passwd = '$passwd'");*/

$result = mysqli_query($db, $user_check_query);
 


$number = $result->num_rows;
$row = mysqli_fetch_assoc($result);
echo $user_check_query;
if ($number >0 && $row['role']==1) {
    header( "Location: http://127.0.0.1:5500/postlogin" );


  }
elseif ($number >0 && $row['role']==0) {
     
        header( "Location: http://127.0.0.1:5500/homepage" );
    }else {$loginid=$_POST['username'];
$password=$_POST['password'];


$password=md5($password);


$user_check_query="SELECT * FROM users WHERE username ='$loginid' AND  password = '$password'";


/*$result = $mysqli->query("SELECT * FROM users WHERE username ='$loginid' AND  passwd = '$passwd'");*/


$result = mysqli_query($db, $user_check_query); 
 


$number = $result->num_rows;
$row = mysqli_fetch_assoc($result);
echo $user_check_query;
if ($number >0 && $row['role']==1) {
    header( "Location: http://localhost:8083/addItems" );


  }
elseif ($number >0 && $row['role']==0) {
      
        header( "Location: http://localhost:8083/homepage" );
    }else {
     ?>
      <script>
    
          alert('The user does not exist');
         
          window.location = 'http://localhost:8083/login';
     </script>
<?php
     
    session_destroy();
    }
   
?>


     ?>
      <script>
   
          alert('The user does not exist');
         
          window.location = 'http://localhost:8083/login';
     </script>
<?php
     
    session_destroy();
    }
   
?>
