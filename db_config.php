<?php
$host = "localhost";
$user = "root"; // اسم المستخدم الافتراضي
$pass = "";     // كلمة المرور الافتراضية
$dbname = "souq_egypt";

$conn = new mysqli($host, $user, $pass, $dbname);

if ($conn->connect_error) {
    die("فشل الاتصال: " . $conn->connect_error);
}
$conn->set_charset("utf8"); // لدعم اللغة العربية
?>
