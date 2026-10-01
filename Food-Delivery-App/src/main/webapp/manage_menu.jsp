<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>Manage Menu - ${restaurant.name}</title>
    <link rel="stylesheet" href="<%= request.getContextPath() %>/css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <h1>Manage Menu - ${restaurant.name}</h1>

    <div class="card">
        <h3>Add a new item</h3>
        <form action="menu" method="post">
            <input type="hidden" name="action" value="add">
            <label>Name</label>
            <input type="text" name="name" required>
            <label>Description</label>
            <input type="text" name="description">
            <label>Price (₹)</label>
            <input type="number" step="0.01" name="price" required>
            <label>Image URL (optional — paste a link to a photo)</label>
            <input type="text" name="imageUrl" placeholder="https://...">
            <button type="submit" class="btn">Add Item</button>
        </form>
    </div>

    <div class="card">
        <h3>Current Menu</h3>
        <table>
            <tr><th>Name</th><th>Price</th><th>Status</th><th></th></tr>
            <c:forEach var="item" items="${items}">
                <tr>
                    <td>${item.name}<br><span class="muted">${item.description}</span></td>
                    <td>₹${item.price}</td>
                    <td>
                        <c:choose>
                            <c:when test="${item.available}"><span class="badge DELIVERED">Available</span></c:when>
                            <c:otherwise><span class="badge CANCELLED">Unavailable</span></c:otherwise>
                        </c:choose>
                    </td>
                    <td>
                        <form action="menu" method="post" class="inline-form">
                            <input type="hidden" name="action" value="toggle">
                            <input type="hidden" name="id" value="${item.id}">
                            <button type="submit" class="btn secondary small">Toggle</button>
                        </form>
                        <form action="menu" method="post" class="inline-form">
                            <input type="hidden" name="action" value="delete">
                            <input type="hidden" name="id" value="${item.id}">
                            <button type="submit" class="btn danger small" onclick="return confirm('Delete this item?')">Delete</button>
                        </form>
                    </td>
                </tr>
            </c:forEach>
        </table>
        <c:if test="${empty items}"><p class="muted">No items yet - add your first one above.</p></c:if>
    </div>
</div>
</body>
</html>
