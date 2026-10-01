package com.upskill.food.servlet;

import com.upskill.food.dao.DeliveryPersonDAO;
import com.upskill.food.dao.OrderDAO;
import com.upskill.food.dao.RestaurantDAO;
import com.upskill.food.model.DeliveryPerson;
import com.upskill.food.model.Order;
import com.upskill.food.model.Restaurant;
import com.upskill.food.model.User;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.util.List;

@WebServlet("/restaurant/dashboard")
public class RestaurantDashboardServlet extends HttpServlet {

    private final RestaurantDAO restaurantDAO = new RestaurantDAO();
    private final OrderDAO orderDAO = new OrderDAO();
    private final DeliveryPersonDAO deliveryPersonDAO = new DeliveryPersonDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        HttpSession session = req.getSession();
        User user = (User) session.getAttribute("user");

        if (!"RESTAURANT".equals(user.getRole())) {
            resp.sendRedirect("restaurants");
            return;
        }

        try {
            Restaurant restaurant = restaurantDAO.getByOwnerId(user.getId());
            List<Order> orders = orderDAO.getByRestaurant(restaurant.getId());
            List<DeliveryPerson> available = deliveryPersonDAO.getAvailable();

            req.setAttribute("restaurant", restaurant);
            req.setAttribute("orders", orders);
            req.setAttribute("availableDeliveryPersons", available);
            req.getRequestDispatcher("/restaurant_dashboard.jsp").forward(req, resp);
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
