package com.upskill.food.servlet;

import com.upskill.food.model.OrderItem;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.Map;

@WebServlet("/cart")
public class CartServlet extends HttpServlet {

    @SuppressWarnings("unchecked")
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        HttpSession session = req.getSession();
        Map<Integer, OrderItem> cart = (Map<Integer, OrderItem>) session.getAttribute("cart");

        BigDecimal total = BigDecimal.ZERO;
        if (cart != null) {
            for (OrderItem item : cart.values()) {
                total = total.add(item.getSubtotal());
            }
        }

        req.setAttribute("cart", cart);
        req.setAttribute("total", total);
        req.getRequestDispatcher("cart.jsp").forward(req, resp);
    }

    @SuppressWarnings("unchecked")
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        HttpSession session = req.getSession();
        Map<Integer, OrderItem> cart = (Map<Integer, OrderItem>) session.getAttribute("cart");
        String action = req.getParameter("action");

        if (cart != null) {
            int foodItemId = Integer.parseInt(req.getParameter("foodItemId"));
            if ("remove".equals(action)) {
                cart.remove(foodItemId);
            } else if ("update".equals(action)) {
                int quantity = Integer.parseInt(req.getParameter("quantity"));
                if (quantity <= 0) {
                    cart.remove(foodItemId);
                } else if (cart.containsKey(foodItemId)) {
                    cart.get(foodItemId).setQuantity(quantity);
                }
            } else if ("clear".equals(action)) {
                cart.clear();
            }
        }

        resp.sendRedirect("cart");
    }
}
