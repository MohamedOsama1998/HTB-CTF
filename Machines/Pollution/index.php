<?php

require '../bootstrap.php';

use app\classes\Routes;
use app\classes\Uri;


$routes = [
    "/" => "controllers/index.php",
    "/login" => "controllers/login.php",
    "/register" => "controllers/register.php",
    "/home" => "controllers/home.php",
    "/admin" => "controllers/admin.php",
    "/api" => "controllers/api.php",
    "/set/role/admin" => "controllers/set_role_admin.php",
    "/logout" => "controllers/logout.php"
];

$uri = Uri::load();
require Routes::load($uri, $routes);
