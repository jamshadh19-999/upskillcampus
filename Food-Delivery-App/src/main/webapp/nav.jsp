<nav>
    <a class="brand" href="<%= request.getContextPath() %>/"> Upskill FoodExpress</a>
    <div>
        <% if (session.getAttribute("user") != null) {
            String role = (String) session.getAttribute("role");
            com.upskill.food.model.User u = (com.upskill.food.model.User) session.getAttribute("user");
        %>
            <span style="color:#fff; margin-right:10px;">Hi, <%= u.getName() %> (<%= role %>)</span>
            <% if ("CUSTOMER".equals(role)) { %>
                <a href="<%= request.getContextPath() %>/restaurants">Restaurants</a>
                <a href="<%= request.getContextPath() %>/cart">Cart</a>
                <a href="<%= request.getContextPath() %>/orders">My Orders</a>
            <% } else if ("RESTAURANT".equals(role)) { %>
                <a href="<%= request.getContextPath() %>/restaurant/dashboard">Orders</a>
                <a href="<%= request.getContextPath() %>/restaurant/menu">Manage Menu</a>
            <% } else if ("DELIVERY".equals(role)) { %>
                <a href="<%= request.getContextPath() %>/delivery/dashboard">My Deliveries</a>
            <% } %>
            <a href="<%= request.getContextPath() %>/logout">Logout</a>
        <% } else { %>
            <a href="<%= request.getContextPath() %>/login.jsp">Login</a>
            <a href="<%= request.getContextPath() %>/register.jsp">Sign Up</a>
        <% } %>
    </div>
</nav>
