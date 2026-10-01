<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>My Orders - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <h1>My Orders</h1>

    <c:if test="${param.placed != null}">
        <div class="alert success">Order #${param.placed} placed successfully!</div>
    </c:if>

    <c:forEach var="o" items="${orders}">
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3>Order #${o.id} &middot; ${o.restaurantName}</h3>
                <span class="badge ${o.status}">${o.status}</span>
            </div>
            <p class="muted">Placed: ${o.createdAt}</p>
            <p>Delivery Address: ${o.deliveryAddress}</p>
            <c:if test="${o.etaMinutes != null}">
                <p><strong>ETA:</strong> ${o.etaMinutes} minutes</p>
            </c:if>
            <c:if test="${o.deliveryPersonName != null}">
                <p><strong>Delivery Partner:</strong> ${o.deliveryPersonName}</p>
            </c:if>
            <p class="price">Total: ₹${o.totalAmount}</p>
        </div>
    </c:forEach>

    <c:if test="${empty orders}">
        <p class="muted">You haven't placed any orders yet.</p>
    </c:if>
</div>
</body>
</html>
