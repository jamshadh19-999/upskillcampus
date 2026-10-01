package com.upskill.food.servlet;

import com.upskill.food.dao.UserDAO;
import com.upskill.food.model.User;
import com.upskill.food.util.PasswordUtil;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;

@WebServlet("/login")
public class LoginServlet extends HttpServlet {

    private final UserDAO userDAO = new UserDAO();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String email = req.getParameter("email");
        String password = req.getParameter("password");

        try {
            User user = userDAO.findByEmailAndPassword(email, PasswordUtil.hash(password));
            if (user == null) {
                resp.sendRedirect("login.jsp?error=Invalid+email+or+password");
                return;
            }

            HttpSession session = req.getSession();
            session.setAttribute("user", user);
            session.setAttribute("role", user.getRole());

            switch (user.getRole()) {
                case "RESTAURANT":
                    resp.sendRedirect("restaurant/dashboard");
                    break;
                case "DELIVERY":
                    resp.sendRedirect("delivery/dashboard");
                    break;
                default:
                    resp.sendRedirect("restaurants");
            }
        } catch (Exception e) {
            e.printStackTrace();
            resp.sendRedirect("login.jsp?error=Login+failed");
        }
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.sendRedirect("login.jsp");
    }
}
