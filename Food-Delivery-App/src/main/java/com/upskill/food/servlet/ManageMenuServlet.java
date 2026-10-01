package com.upskill.food.servlet;

import com.upskill.food.dao.FoodItemDAO;
import com.upskill.food.dao.RestaurantDAO;
import com.upskill.food.model.FoodItem;
import com.upskill.food.model.Restaurant;
import com.upskill.food.model.User;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.List;

@WebServlet("/restaurant/menu")
public class ManageMenuServlet extends HttpServlet {

    private final FoodItemDAO foodItemDAO = new FoodItemDAO();
    private final RestaurantDAO restaurantDAO = new RestaurantDAO();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        User user = (User) req.getSession().getAttribute("user");
        try {
            Restaurant restaurant = restaurantDAO.getByOwnerId(user.getId());
            List<FoodItem> items = foodItemDAO.getByRestaurant(restaurant.getId());
            req.setAttribute("restaurant", restaurant);
            req.setAttribute("items", items);
            req.getRequestDispatcher("/manage_menu.jsp").forward(req, resp);
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        User user = (User) req.getSession().getAttribute("user");
        String action = req.getParameter("action");

        try {
            Restaurant restaurant = restaurantDAO.getByOwnerId(user.getId());

            if ("add".equals(action)) {
                FoodItem item = new FoodItem();
                item.setRestaurantId(restaurant.getId());
                item.setName(req.getParameter("name"));
                item.setDescription(req.getParameter("description"));
                item.setPrice(new BigDecimal(req.getParameter("price")));
                item.setAvailable(true);
                item.setImageUrl(req.getParameter("imageUrl"));
                foodItemDAO.createFoodItem(item);
            } else if ("toggle".equals(action)) {
                int id = Integer.parseInt(req.getParameter("id"));
                FoodItem item = foodItemDAO.getById(id);
                item.setAvailable(!item.isAvailable());
                foodItemDAO.updateFoodItem(item);
            } else if ("delete".equals(action)) {
                int id = Integer.parseInt(req.getParameter("id"));
                foodItemDAO.deleteFoodItem(id);
            }

            resp.sendRedirect("menu");
        } catch (Exception e) {
            throw new ServletException(e);
        }
    }
}
