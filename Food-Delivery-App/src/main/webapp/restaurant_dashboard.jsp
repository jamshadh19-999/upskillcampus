<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>${restaurant.name} - Dashboard</title>
    <link rel="stylesheet" href="<%= request.getContextPath() %>/css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <h1>${restaurant.name} - Incoming Orders</h1>

    <c:forEach var="o" items="${orders}">
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3>Order #${o.id} &middot; ${o.customerName}</h3>
                <span class="badge ${o.status}">${o.status}</span>
            </div>
            <p>Deliver to: ${o.deliveryAddress}</p>
            <p class="price">Total: ₹${o.totalAmount}</p>

            <c:if test="${o.status == 'PLACED'}">
                <form action="orders/action" method="post" class="form-wide">
                    <input type="hidden" name="orderId" value="${o.id}">
                    <input type="hidden" name="action" value="accept">

                    <label>Assign Delivery Person</label>
                    <select name="deliveryPersonId" required>
                        <c:forEach var="dp" items="${availableDeliveryPersons}">
                            <option value="${dp.id}">${dp.name} (${dp.phone})</option>
                        </c:forEach>
                    </select>

                    <label>ETA (minutes)</label>
                    <input type="number" name="etaMinutes" min="1" value="30" required>

                    <button type="submit" class="btn">Accept &amp; Assign</button>
                </form>
                <form action="orders/action" method="post" class="inline-form" onsubmit="return confirm('Cancel this order?')">
                    <input type="hidden" name="orderId" value="${o.id}">
                    <input type="hidden" name="action" value="cancel">
                    <button type="submit" class="btn danger small">Cancel Order</button>
                </form>
                <c:if test="${empty availableDeliveryPersons}">
                    <p class="muted">No delivery persons are currently available.</p>
                </c:if>
            </c:if>

            <c:if test="${o.status != 'PLACED'}">
                <p class="muted">
                    <c:if test="${o.deliveryPersonName != null}">Assigned to ${o.deliveryPersonName}. </c:if>
                    <c:if test="${o.etaMinutes != null}">ETA: ${o.etaMinutes} min.</c:if>
                </p>
            </c:if>
        </div>
    </c:forEach>

    <c:if test="${empty orders}">
        <p class="muted">No orders yet.</p>
    </c:if>
</div>
</body>
</html>
