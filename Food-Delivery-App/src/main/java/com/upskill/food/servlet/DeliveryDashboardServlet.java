package com.upskill.food.servlet;

import com.upskill.food.dao.DeliveryPersonDAO;
import com.upskill.food.dao.OrderDAO;
import com.upskill.food.model.DeliveryPerson;
import com.upskill.food.model.Order;
import com.upskill.food.model.User;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.util.List;

@WebServlet("/delivery/dashboard")
public class DeliveryDashboardServlet extends HttpServlet {

    private final DeliveryPersonDAO deliveryPersonDAO = new DeliveryPersonDAO();
    private final OrderDAO orderDAO = new OrderDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        User user = (User) req.getSession().getAttribute("user");
        try {
            DeliveryPerson dp = deliveryPersonDAO.getByUserId(user.getId());
            List<Order> orders = orderDAO.getByDeliveryPerson(dp.getId());
            req.setAttribute("deliveryPerson", dp);
            req.setAttribute("orders", orders);
            req.getRequestDispatcher("/delivery_dashboard.jsp").forward(req, resp);
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        User user = (User) req.getSession().getAttribute("user");
        String action = req.getParameter("action");

        try {
            int orderId = Integer.parseInt(req.getParameter("orderId"));

            if ("pickup".equals(action)) {
                orderDAO.updateStatus(orderId, "OUT_FOR_DELIVERY");
            } else if ("delivered".equals(action)) {
                orderDAO.updateStatus(orderId, "DELIVERED");
                DeliveryPerson dp = deliveryPersonDAO.getByUserId(user.getId());
                deliveryPersonDAO.updateStatus(dp.getId(), "AVAILABLE");
            }

            resp.sendRedirect("dashboard");
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
