<%@ page isErrorPage="true" %>
<!DOCTYPE html>
<html>
<head>
    <title>Error - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
<div class="container">
    <div class="card">
        <h2>Something went wrong</h2>
        <p class="muted"><%= exception != null ? exception.toString() : "Unknown error" %></p>
        <a class="btn" href="<%= request.getContextPath() %>/">Go Home</a>
    </div>
</div>
</body>
</html>
