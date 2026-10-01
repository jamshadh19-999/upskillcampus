# Food Delivery App — UpSkill Academy Internship Project

A full-stack Java web app: **Servlets + JSP + JDBC**, built as a Maven project.

## What's inside
- **Customer**: sign up, browse restaurants, view menus, add to cart, place orders, track order status + ETA.
- **Restaurant owner**: sign up (auto-creates their restaurant), manage menu items, view incoming orders,
  accept an order + assign a delivery person + set an ETA in one step.
- **Delivery person**: sign up, see assigned orders, mark "picked up" and "delivered".
- Order lifecycle: `PLACED → CONFIRMED → OUT_FOR_DELIVERY → DELIVERED` (or `CANCELLED`).

## Tech stack
| Layer | Technology |
|---|---|
| Frontend | JSP + JSTL, plain CSS |
| Backend | Java Servlets (javax.servlet, annotation-based `@WebServlet`) |
| Data access | Plain JDBC (`PreparedStatement`, no ORM) |
| Database | **H2** — file-based, pure Java, zero install |
| Server | **Embedded Tomcat 7** via a Maven plugin — zero install |
| Build | Maven |

## ⬇️ What you need to install
Just **two things**:

1. **JDK 11 or newer** — https://adoptium.net/ (pick "Temurin 11" or later)
2. **Apache Maven** — https://maven.apache.org/download.cgi (add it to your PATH)

That's it. You do **not** need to separately install:
- ❌ Tomcat (it's launched in-process by the `tomcat7-maven-plugin` when you run `mvn tomcat7:run`)
- ❌ MySQL / XAMPP / any database server (H2 stores everything in a local file, `./data/fooddb.mv.db`,
  created automatically on first run)

Check your installs:
```bash
java -version
mvn -version
```

## How to run
From inside the `food-delivery-app` folder:
```bash
mvn tomcat7:run
```
The first run will download the project's dependencies (needs internet once) and then start the app at:
```
http://localhost:8080/
```
Stop it any time with `Ctrl+C`. Your data persists in the `data/` folder between runs — delete that folder
if you want to reset the database.

## Trying it out
1. Go to `http://localhost:8080/register.jsp`, create a **Restaurant Owner** account (a restaurant is
   auto-created for you), and add a few menu items under "Manage Menu".
2. Create a **Delivery Person** account (a second browser / incognito window is handy).
3. Create a **Customer** account, browse restaurants, add items to your cart and place an order.
4. Log back in as the restaurant owner → accept the order, assign the delivery person, set an ETA.
5. Log in as the delivery person → mark it picked up, then delivered.
6. Log back in as the customer → watch the order status update.

## Project structure
```
food-delivery-app/
├── pom.xml
├── README.md
└── src/main/
    ├── java/com/upskill/food/
    │   ├── model/       User, Restaurant, FoodItem, DeliveryPerson, Order, OrderItem
    │   ├── dao/         JDBC data-access classes (one per table, PreparedStatements only)
    │   ├── util/        DBUtil (connection), PasswordUtil (SHA-256 hashing)
    │   ├── listener/     AppInitListener - runs schema.sql on startup
    │   ├── filter/       AuthFilter - blocks pages that require login
    │   └── servlet/      One servlet per feature (register, login, cart, checkout, etc.)
    ├── resources/
    │   └── schema.sql    Table definitions (auto-run on startup)
    └── webapp/
        ├── *.jsp          All the pages
        ├── css/style.css
        └── WEB-INF/web.xml
```

## Notes / what to mention if asked "what would you add next"
The spec image mentions several stretch features that a real production app would need but this MVP
intentionally leaves out to keep the internship scope manageable:
- Live GPS map tracking (would need a mapping API like Google Maps/Mapbox)
- Online payment gateway integration (currently pay on delivery / cash assumed)
- Ratings & reviews, favorites/recent orders, personalized recommendations
- Push notifications (currently the customer just refreshes the "My Orders" page)
- An admin panel for platform-wide analytics

These are good "future enhancements" talking points if your mentor asks about the roadmap.
