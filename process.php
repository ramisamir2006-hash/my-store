<?php
include 'db_config.php';

// إضافة منتج جديد
if(isset($_POST['action']) && $_POST['action'] == 'add_product') {
    $pName = $_POST['pName'];
    $pCat = $_POST['pCat'];
    $pShip = $_POST['pShip'];

    $sql = "INSERT INTO products (product_name, category_name, shipping_method) VALUES ('$pName', '$pCat', '$pShip')";
    
    if ($conn->query($sql) === TRUE) {
        echo "success";
    } else {
        echo "error";
    }
}

// جلب المنتجات لعرضها
if(isset($_GET['action']) && $_GET['action'] == 'get_products') {
    $result = $conn->query("SELECT * FROM products ORDER BY id DESC");
    $products = [];
    while($row = $result->fetch_assoc()) {
        $products[] = $row;
    }
    echo json_encode($products);
}
?>
