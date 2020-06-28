<!DOCTYPE html>
<html>
<head>
<title>Submit Page</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {
  box-sizing: border-box;
}
body{
font-family:verdana;
}
input[type=text], select, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
background: rgb(100,100,100);
color:white;
font-family:verdana;
font-size:15px;

}
a:link, a:visited {
  background-color: #4CAF50;
  color: white;
  padding: 14px 25px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  border-radius: 4px;
  transition: 0.3s;
}

a:hover, a:active {
  color: white;
  background-color: red;
  border-radius: 1px;
}

h2{
color:white;
}
p{
color:white;
}
label {
	color:white;
  padding: 12px 12px 12px 0;
  display: inline-block;
}
input[type=submit] {
  background-color: #4CAF50;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  float: right;
  transition: 0.3s;
}

input[type=submit]:hover {
  background-color: red;
  border-radius: 1px;
}

.container {
  border-radius: 5px;
  background-color: rgb(50,50,50);
  padding: 20px;
}

.col-25 {
  float: left;
  width: 25%;
  margin-top: 6px;
}

.col-75 {
  float: left;
  width: 75%;
  margin-top: 6px;
}

/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}

/* Responsive layout - when the screen is less than 600px wide, make the two columns stack on top of each other instead of next to each other */
@media screen and (max-width: 600px) {
  .col-25, .col-75, input[type=submit] {
    width: 100%;
    margin-top: 0;
  }
}
</style>
</head>
<body style="background:black;text-align:center;">

<h2>Request Form</h2>
<p>Enter the each URL in a new line.</p>

<div class="container">
  <form method="post" action="/write.php">
    
    <div class="row">
      <div class="col-25">
        <label for="subject">Submissons</label>
      </div>
      <div class="col-75">
        <textarea id="subject" name="subject" placeholder="Enter each URL in a new line" style="height:200px"></textarea>
      </div>
    </div>
    <div class="row">
      <input type="submit" value="Submit">
    </div>
  </form>
</div>
	<a href="http://www.yourhub.tk">Back to Homepage</a>
</div>
</div>

</body>
</html>