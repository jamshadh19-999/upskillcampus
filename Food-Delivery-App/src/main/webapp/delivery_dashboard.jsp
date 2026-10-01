<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>My Deliveries - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="<%= request.getContextPath() %>/css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <h1>My Deliveries</h1>
    <p class="muted">Status: <span class="badge DELIVERED">${deliveryPerson.status}</span></p>

    <c:forEach var="o" items="${orders}">
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3>Order #${o.id} &middot; ${o.restaurantName}</h3>
                <span class="badge ${o.status}">${o.status}</span>
            </div>
            <p><strong>Customer:</strong> ${o.customerName}</p>
            <p><strong>Deliver to:</strong> ${o.deliveryAddress}</p>
            <p><strong>ETA:</strong> ${o.etaMinutes} minutes</p>

            <c:if test="${o.status == 'CONFIRMED'}">
                <form action="dashboard" method="post" class="inline-form">
                    <input type="hidden" name="orderId" value="${o.id}">
                    <input type="hidden" name="action" value="pickup">
                    <button type="submit" class="btn">Mark Picked Up</button>
                </form>
            </c:if>
            <c:if test="${o.status == 'OUT_FOR_DELIVERY'}">
                <form action="dashboard" method="post" class="inline-form">
                    <input type="hidden" name="orderId" value="${o.id}">
                    <input type="hidden" name="action" value="delivered">
                    <button type="submit" class="btn">Mark Delivered</button>
                </form>
            </c:if>
        </div>
    </c:forEach>

    <c:if test="${empty orders}">
        <p class="muted">No active deliveries assigned to you right now.</p>
    </c:if>
</div>
</body>
</html>
