<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>Your Cart - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <h1>Your Cart</h1>

    <c:if test="${param.error != null}">
        <div class="alert error">${param.error}</div>
    </c:if>

    <c:choose>
        <c:when test="${empty cart}">
            <div class="card"><p class="muted">Your cart is empty. <a href="restaurants">Browse restaurants</a></p></div>
        </c:when>
        <c:otherwise>
            <div class="card">
                <table>
                    <tr><th>Item</th><th>Price</th><th>Qty</th><th>Subtotal</th><th></th></tr>
                    <c:forEach var="entry" items="${cart}">
                        <tr>
                            <td>${entry.value.foodName}</td>
                            <td>₹${entry.value.price}</td>
                            <td>
                                <form action="cart" method="post" class="inline-form">
                                    <input type="hidden" name="action" value="update">
                                    <input type="hidden" name="foodItemId" value="${entry.key}">
                                    <input type="number" name="quantity" value="${entry.value.quantity}" min="0" style="width:60px;" onchange="this.form.submit()">
                                </form>
                            </td>
                            <td>₹${entry.value.subtotal}</td>
                            <td>
                                <form action="cart" method="post" class="inline-form">
                                    <input type="hidden" name="action" value="remove">
                                    <input type="hidden" name="foodItemId" value="${entry.key}">
                                    <button type="submit" class="btn danger small">Remove</button>
                                </form>
                            </td>
                        </tr>
                    </c:forEach>
                </table>
                <h3 style="text-align:right;">Total: <span class="price">₹${total}</span></h3>
            </div>

            <div class="card">
                <h3>Delivery Address</h3>
                <form action="checkout" method="post">
                    <input type="text" name="deliveryAddress" placeholder="Leave blank to use your profile address">
                    <button type="submit" class="btn">Place Order</button>
                </form>
            </div>
        </c:otherwise>
    </c:choose>
</div>
</body>
</html>
