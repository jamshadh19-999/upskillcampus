package com.upskill.food.servlet;

import com.upskill.food.dao.FoodItemDAO;
import com.upskill.food.dao.RestaurantDAO;
import com.upskill.food.model.FoodItem;
import com.upskill.food.model.OrderItem;
import com.upskill.food.model.Restaurant;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@WebServlet("/menu")
public class MenuServlet extends HttpServlet {

    private final FoodItemDAO foodItemDAO = new FoodItemDAO();
    private final RestaurantDAO restaurantDAO = new RestaurantDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            int restaurantId = Integer.parseInt(req.getParameter("restaurantId"));
            Restaurant restaurant = restaurantDAO.getById(restaurantId);
            List<FoodItem> items = foodItemDAO.getByRestaurant(restaurantId);
            req.setAttribute("restaurant", restaurant);
            req.setAttribute("items", items);
            req.getRequestDispatcher("menu.jsp").forward(req, resp);
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }

    @SuppressWarnings("unchecked")
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        // Add-to-cart: cart is kept in the session as Map<foodItemId, OrderItem>
        HttpSession session = req.getSession();
        if (session.getAttribute("user") == null) {
            resp.sendRedirect("login.jsp?error=Please+log+in+to+order");
            return;
        }

        try {
            int foodItemId = Integer.parseInt(req.getParameter("foodItemId"));
            int quantity = Integer.parseInt(req.getParameter("quantity"));
            int restaurantId = Integer.parseInt(req.getParameter("restaurantId"));

            FoodItem item = foodItemDAO.getById(foodItemId);

            Map<Integer, OrderItem> cart = (Map<Integer, OrderItem>) session.getAttribute("cart");
            Integer cartRestaurantId = (Integer) session.getAttribute("cartRestaurantId");

            // A cart can only hold items from one restaurant at a time
            if (cart == null || cartRestaurantId == null || cartRestaurantId != restaurantId) {
                cart = new LinkedHashMap<>();
                session.setAttribute("cartRestaurantId", restaurantId);
            }

            if (cart.containsKey(foodItemId)) {
                OrderItem existing = cart.get(foodItemId);
                existing.setQuantity(existing.getQuantity() + quantity);
            } else {
                cart.put(foodItemId, new OrderItem(foodItemId, item.getName(), quantity, item.getPrice()));
            }

            session.setAttribute("cart", cart);
            resp.sendRedirect("menu?restaurantId=" + restaurantId + "&added=1");
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
