<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>${restaurant.name} - Menu</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <a href="restaurants" class="muted">&larr; Back to restaurants</a>
    <h1>${restaurant.name}</h1>
    <p class="muted">${restaurant.cuisine} &middot; ${restaurant.address}</p>

    <c:if test="${param.added == '1'}">
        <div class="alert success">Added to cart!</div>
    </c:if>

    <div class="grid">
        <c:forEach var="item" items="${items}">
            <c:if test="${item.available}">
                <div class="card">
                    <c:if test="${not empty item.imageUrl}">
                        <img src="${item.imageUrl}" alt="${item.name}" style="width:100%; height:140px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
                    </c:if>
                    <h3>${item.name}</h3>
                    <p class="muted">${item.description}</p>
                    <p class="price">₹${item.price}</p>
                    <form action="menu" method="post">
                        <input type="hidden" name="foodItemId" value="${item.id}">
                        <input type="hidden" name="restaurantId" value="${restaurant.id}">
                        <input type="number" name="quantity" value="1" min="1" style="width:70px; display:inline-block;">
                        <button type="submit" class="btn small">Add to Cart</button>
                    </form>
                </div>
            </c:if>
        </c:forEach>

        <c:if test="${empty items}">
            <p class="muted">This restaurant hasn't added any menu items yet.</p>
        </c:if>
    </div>
</div>
</body>
</html>
