<html>
<h1> It's working</h1>
</html>
<?php
file_put_contents('submit.txt', file_get_contents('php://input'),FILE_APPEND);
$fp = fopen('submit.txt','a');
fwrite($fp, "\n\n");
fclose($fp);
?>
