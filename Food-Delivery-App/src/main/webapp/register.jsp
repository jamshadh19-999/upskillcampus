<!DOCTYPE html>
<html>
<head>
    <title>Sign Up - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container" style="max-width:460px;">
    <div class="card">
        <h2>Create an account</h2>

        <% if (request.getAttribute("error") != null) { %>
            <div class="alert error"><%= request.getAttribute("error") %></div>
        <% } %>

        <form action="register" method="post">
            <label>I am a</label>
            <select name="role" id="role" onchange="toggleFields()">
                <option value="CUSTOMER">Customer (order food)</option>
                <option value="RESTAURANT">Restaurant Owner</option>
                <option value="DELIVERY">Delivery Person</option>
            </select>

            <label>Full Name</label>
            <input type="text" name="name" required>

            <label>Email</label>
            <input type="email" name="email" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <label>Phone</label>
            <input type="text" name="phone" required>

            <label>Address</label>
            <input type="text" name="address" required>

            <div id="restaurantFields" style="display:none;">
                <label>Restaurant Name</label>
                <input type="text" name="restaurantName">

                <label>Cuisine Type</label>
                <input type="text" name="cuisine" placeholder="e.g. Indian, Italian, Fast Food">
            </div>

            <button type="submit" class="btn">Create Account</button>
        </form>
        <p class="muted">Already have an account? <a href="login.jsp">Login</a></p>
    </div>
</div>

<script>
function toggleFields() {
    var role = document.getElementById('role').value;
    document.getElementById('restaurantFields').style.display = (role === 'RESTAURANT') ? 'block' : 'none';
}
</script>
</body>
</html>
