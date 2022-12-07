<?php
require './bootstrap.php';


if (!isset($_SESSION['auth']) or $_SESSION['auth'] != True) {
    die(header('Location: /login.php'));
}

if (!isset($_GET['page']) or empty($_GET['page'])) {
    die(header('Location: /?page=home'));
}

$view = 1;

?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="assets/js/tailwind.js"></script>
    <title>Developers Collect</title>
</head>

<body>
    <div class="flex flex-col h-screen justify-between">
        <?php include("header.php"); ?>
        
        <main class="mb-auto mx-24">
            <?php include($_GET['page'] . ".php"); ?>
        </main>

        <?php include("footer.php"); ?>
    </div>

</body>

</html>