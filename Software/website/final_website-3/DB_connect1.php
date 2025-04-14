<?php

$hostname= "localhost";
$username="root";
$dbname ="rakusens";
$password= "";

//$mysqli = new mysqli($hostname, $username, $password,$dbname);

$db = mysqli_connect($hostname, $username, $password, $dbname);

// Check connection
if($db === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}
 
?>
