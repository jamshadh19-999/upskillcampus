<%
    if (session.getAttribute("user") != null) {
        String role = (String) session.getAttribute("role");
        if ("RESTAURANT".equals(role)) {
            response.sendRedirect("restaurant/dashboard");
        } else if ("DELIVERY".equals(role)) {
            response.sendRedirect("delivery/dashboard");
        } else {
            response.sendRedirect("restaurants");
        }
    } else {
        response.sendRedirect("login.jsp");
    }
%>
