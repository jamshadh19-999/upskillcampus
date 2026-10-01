package com.upskill.food.servlet;

import com.upskill.food.dao.OrderDAO;
import com.upskill.food.model.Order;
import com.upskill.food.model.OrderItem;
import com.upskill.food.model.User;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@WebServlet("/checkout")
public class CheckoutServlet extends HttpServlet {

    private final OrderDAO orderDAO = new OrderDAO();

    @SuppressWarnings("unchecked")
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        HttpSession session = req.getSession();
        User user = (User) session.getAttribute("user");
        Map<Integer, OrderItem> cart = (Map<Integer, OrderItem>) session.getAttribute("cart");
        Integer restaurantId = (Integer) session.getAttribute("cartRestaurantId");

        if (cart == null || cart.isEmpty() || restaurantId == null) {
            resp.sendRedirect("cart?error=Your+cart+is+empty");
            return;
        }

        String deliveryAddress = req.getParameter("deliveryAddress");
        if (deliveryAddress == null || deliveryAddress.trim().isEmpty()) {
            deliveryAddress = user.getAddress();
        }

        BigDecimal total = BigDecimal.ZERO;
        List<OrderItem> items = new ArrayList<>(cart.values());
        for (OrderItem item : items) {
            total = total.add(item.getSubtotal());
        }

        Order order = new Order();
        order.setCustomerId(user.getId());
        order.setRestaurantId(restaurantId);
        order.setTotalAmount(total);
        order.setDeliveryAddress(deliveryAddress);

        try {
            int orderId = orderDAO.createOrder(order, items);
            // clear cart after successful order
            session.removeAttribute("cart");
            session.removeAttribute("cartRestaurantId");
            resp.sendRedirect("orders?placed=" + orderId);
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
