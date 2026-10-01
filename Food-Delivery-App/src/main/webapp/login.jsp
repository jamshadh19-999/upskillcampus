<!DOCTYPE html>
<html>
<head>
    <title>Login - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container" style="max-width:420px;">
    <div class="card">
        <h2>Login</h2>

        <% String error = request.getParameter("error"); %>
        <% if (error != null) { %>
            <div class="alert error"><%= error %></div>
        <% } %>
        <% String success = request.getParameter("success"); %>
        <% if (success != null) { %>
            <div class="alert success"><%= success %></div>
        <% } %>

        <form action="login" method="post">
            <label>Email</label>
            <input type="email" name="email" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit" class="btn">Login</button>
        </form>
        <p class="muted">Don't have an account? <a href="register.jsp">Sign up here</a></p>
    </div>
</div>
</body>
</html>
