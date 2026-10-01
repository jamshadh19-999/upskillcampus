package com.upskill.food.servlet;

import com.upskill.food.dao.DeliveryPersonDAO;
import com.upskill.food.dao.OrderDAO;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebServlet("/restaurant/orders/action")
public class OrderActionServlet extends HttpServlet {

    private final OrderDAO orderDAO = new OrderDAO();
    private final DeliveryPersonDAO deliveryPersonDAO = new DeliveryPersonDAO();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            int orderId = Integer.parseInt(req.getParameter("orderId"));
            String action = req.getParameter("action");

            if ("accept".equals(action)) {
                int deliveryPersonId = Integer.parseInt(req.getParameter("deliveryPersonId"));
                int etaMinutes = Integer.parseInt(req.getParameter("etaMinutes"));
                orderDAO.confirmAndAssign(orderId, deliveryPersonId, etaMinutes);
                deliveryPersonDAO.updateStatus(deliveryPersonId, "BUSY");
            } else if ("cancel".equals(action)) {
                orderDAO.updateStatus(orderId, "CANCELLED");
            }

            resp.sendRedirect("../dashboard");
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
