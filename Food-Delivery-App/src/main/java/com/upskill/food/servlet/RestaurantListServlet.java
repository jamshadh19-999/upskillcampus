package com.upskill.food.servlet;

import com.upskill.food.dao.RestaurantDAO;
import com.upskill.food.model.Restaurant;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;

@WebServlet("/restaurants")
public class RestaurantListServlet extends HttpServlet {

    private final RestaurantDAO restaurantDAO = new RestaurantDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            List<Restaurant> restaurants = restaurantDAO.getAllRestaurants();
            req.setAttribute("restaurants", restaurants);
            req.getRequestDispatcher("restaurants.jsp").forward(req, resp);
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
