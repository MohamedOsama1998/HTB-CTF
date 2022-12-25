<?php

include "header.php";

function createTimeChannel()
{
    sleep(1);
}

include "db_conn.php";

if (isset($_SESSION['userid'])){
    header('Location: ./index.php');
    die();
}


if (isset($_GET['login'])) {
    $username = $_POST['user'];
    $password = $_POST['password'];

    $statement = $pdo->prepare("SELECT * FROM users WHERE username = :username");
    $result = $statement->execute(array('username' => $username));
    $user = $statement->fetch();

    if ($user !== false) {
        createTimeChannel();
        if (password_verify($password, $user['password'])) {
            $_SESSION['userid'] = $user['id'];
            $_SESSION['role'] = $user['role'];
	    header('Location: ./index.php');
            return;
        }
    }
    $errorMessage = "Invalid username or password entered";


}
?>
<?php
if (isset($errorMessage)) {

    ?>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-10 col-md-offset-1">
                <div class="alert alert-danger alert-dismissible fade in text-center" role="alert"><strong>

                        <?php echo $errorMessage; ?>

                </div>
            </div>
        </div>
    </div>
    <?php
}
?>
    <link rel="stylesheet" href="./css/login.css">

    <div class="wrapper fadeInDown">
        <div id="formContent">
            <div class="fadeIn first" style="padding: 20px">
                <img src="./images/user-icon.png" width="100" height="100"/>
            </div>

            <form action="?login=true" method="POST">

                <input type="text" id="login" class="fadeIn second" name="user" placeholder="login">

                <input type="text" id="password" class="fadeIn third" name="password" placeholder="password">

                <input type="submit" class="fadeIn fourth" value="Log In">

            </form>


            <!-- todo -->
            <div id="formFooter">
                <a class="underlineHover" href="#">Forgot Password?</a>
            </div>

        </div>
    </div>


<?php
include "footer.php";
