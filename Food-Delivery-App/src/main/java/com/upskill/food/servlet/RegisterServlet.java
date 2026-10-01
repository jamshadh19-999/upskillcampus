package com.upskill.food.servlet;

import com.upskill.food.dao.DeliveryPersonDAO;
import com.upskill.food.dao.RestaurantDAO;
import com.upskill.food.dao.UserDAO;
import com.upskill.food.model.DeliveryPerson;
import com.upskill.food.model.Restaurant;
import com.upskill.food.model.User;
import com.upskill.food.util.PasswordUtil;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebServlet("/register")
public class RegisterServlet extends HttpServlet {

    private final UserDAO userDAO = new UserDAO();
    private final RestaurantDAO restaurantDAO = new RestaurantDAO();
    private final DeliveryPersonDAO deliveryPersonDAO = new DeliveryPersonDAO();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String name = req.getParameter("name");
        String email = req.getParameter("email");
        String password = req.getParameter("password");
        String role = req.getParameter("role");
        String phone = req.getParameter("phone");
        String address = req.getParameter("address");

        try {
            if (userDAO.emailExists(email)) {
                req.setAttribute("error", "An account with this email already exists.");
                req.getRequestDispatcher("register.jsp").forward(req, resp);
                return;
            }

            User user = new User();
            user.setName(name);
            user.setEmail(email);
            user.setPassword(PasswordUtil.hash(password));
            user.setRole(role);
            user.setPhone(phone);
            user.setAddress(address);

            int userId = userDAO.createUser(user);

            if ("RESTAURANT".equals(role)) {
                String restaurantName = req.getParameter("restaurantName");
                String cuisine = req.getParameter("cuisine");
                Restaurant r = new Restaurant(0, userId, restaurantName, cuisine, address,
                        "Welcome to " + restaurantName);
                restaurantDAO.createRestaurant(r);
            } else if ("DELIVERY".equals(role)) {
                DeliveryPerson dp = new DeliveryPerson(0, userId, name, phone, "AVAILABLE");
                deliveryPersonDAO.createDeliveryPerson(dp);
            }

            resp.sendRedirect("login.jsp?success=Account+created.+Please+log+in.");
        } catch (Exception e) {
            e.printStackTrace();
            req.setAttribute("error", "Something went wrong: " + e.getMessage());
            req.getRequestDispatcher("register.jsp").forward(req, resp);
        }
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.sendRedirect("register.jsp");
    }
}
