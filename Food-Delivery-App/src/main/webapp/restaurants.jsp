<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>Restaurants - UpSkill FoodExpress</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<jsp:include page="nav.jsp"/>
<div class="container">
    <h1>Restaurants near you</h1>

    <div class="grid">
        <c:forEach var="r" items="${restaurants}">
            <div class="card">
                <h3>${r.name}</h3>
                <p class="muted">${r.cuisine} &middot; ${r.address}</p>
                <p>${r.description}</p>
                <a class="btn" href="menu?restaurantId=${r.id}">View Menu</a>
            </div>
        </c:forEach>

        <c:if test="${empty restaurants}">
            <p class="muted">No restaurants have signed up yet. Check back soon!</p>
        </c:if>
    </div>
</div>
</body>
</html>
