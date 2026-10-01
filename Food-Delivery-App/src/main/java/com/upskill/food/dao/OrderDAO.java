package com.upskill.food.dao;

import com.upskill.food.model.Order;
import com.upskill.food.model.OrderItem;
import com.upskill.food.util.DBUtil;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class OrderDAO {

    public int createOrder(Order order, List<OrderItem> items) throws SQLException {
        String orderSql = "INSERT INTO orders (customer_id, restaurant_id, status, total_amount, delivery_address) VALUES (?, ?, 'PLACED', ?, ?)";
        String itemSql = "INSERT INTO order_items (order_id, food_item_id, food_name, quantity, price) VALUES (?, ?, ?, ?, ?)";

        try (Connection conn = DBUtil.getConnection()) {
            conn.setAutoCommit(false);
            int orderId;
            try (PreparedStatement ps = conn.prepareStatement(orderSql, Statement.RETURN_GENERATED_KEYS)) {
                ps.setInt(1, order.getCustomerId());
                ps.setInt(2, order.getRestaurantId());
                ps.setBigDecimal(3, order.getTotalAmount());
                ps.setString(4, order.getDeliveryAddress());
                ps.executeUpdate();
                try (ResultSet rs = ps.getGeneratedKeys()) {
                    rs.next();
                    orderId = rs.getInt(1);
                }
            }

            try (PreparedStatement ps = conn.prepareStatement(itemSql)) {
                for (OrderItem item : items) {
                    ps.setInt(1, orderId);
                    ps.setInt(2, item.getFoodItemId());
                    ps.setString(3, item.getFoodName());
                    ps.setInt(4, item.getQuantity());
                    ps.setBigDecimal(5, item.getPrice());
                    ps.addBatch();
                }
                ps.executeBatch();
            }

            conn.commit();
            return orderId;
        }
    }

    public List<Order> getByCustomer(int customerId) throws SQLException {
        String sql = "SELECT o.*, r.name AS restaurant_name, dp.name AS delivery_name " +
                "FROM orders o JOIN restaurants r ON o.restaurant_id = r.id " +
                "LEFT JOIN delivery_persons dp ON o.delivery_person_id = dp.id " +
                "WHERE o.customer_id = ? ORDER BY o.created_at DESC";
        return queryOrders(sql, customerId);
    }

    public List<Order> getByRestaurant(int restaurantId) throws SQLException {
        String sql = "SELECT o.*, u.name AS customer_name, dp.name AS delivery_name " +
                "FROM orders o JOIN users u ON o.customer_id = u.id " +
                "LEFT JOIN delivery_persons dp ON o.delivery_person_id = dp.id " +
                "WHERE o.restaurant_id = ? ORDER BY o.created_at DESC";
        return queryOrders(sql, restaurantId);
    }

    public List<Order> getByDeliveryPerson(int deliveryPersonId) throws SQLException {
        String sql = "SELECT o.*, u.name AS customer_name, r.name AS restaurant_name " +
                "FROM orders o JOIN users u ON o.customer_id = u.id " +
                "JOIN restaurants r ON o.restaurant_id = r.id " +
                "WHERE o.delivery_person_id = ? AND o.status IN ('CONFIRMED','OUT_FOR_DELIVERY') " +
                "ORDER BY o.created_at DESC";
        return queryOrders(sql, deliveryPersonId);
    }

    private List<Order> queryOrders(String sql, int param) throws SQLException {
        List<Order> list = new ArrayList<>();
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, param);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    list.add(mapRow(rs));
                }
            }
        }
        return list;
    }

    public Order getById(int id) throws SQLException {
        String sql = "SELECT o.*, u.name AS customer_name, r.name AS restaurant_name, dp.name AS delivery_name " +
                "FROM orders o JOIN users u ON o.customer_id = u.id " +
                "JOIN restaurants r ON o.restaurant_id = r.id " +
                "LEFT JOIN delivery_persons dp ON o.delivery_person_id = dp.id " +
                "WHERE o.id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    Order o = mapRow(rs);
                    o.setItems(getItems(id));
                    return o;
                }
            }
        }
        return null;
    }

    public List<OrderItem> getItems(int orderId) throws SQLException {
        List<OrderItem> items = new ArrayList<>();
        String sql = "SELECT * FROM order_items WHERE order_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, orderId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    OrderItem item = new OrderItem(
                            rs.getInt("food_item_id"),
                            rs.getString("food_name"),
                            rs.getInt("quantity"),
                            rs.getBigDecimal("price")
                    );
                    item.setId(rs.getInt("id"));
                    item.setOrderId(orderId);
                    items.add(item);
                }
            }
        }
        return items;
    }

    /** Restaurant accepts the order and assigns a delivery person + ETA in one step. */
    public void confirmAndAssign(int orderId, int deliveryPersonId, int etaMinutes) throws SQLException {
        String sql = "UPDATE orders SET status='CONFIRMED', delivery_person_id=?, eta_minutes=? WHERE id=?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, deliveryPersonId);
            ps.setInt(2, etaMinutes);
            ps.setInt(3, orderId);
            ps.executeUpdate();
        }
    }

    public void updateStatus(int orderId, String status) throws SQLException {
        String sql = "UPDATE orders SET status=? WHERE id=?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, status);
            ps.setInt(2, orderId);
            ps.executeUpdate();
        }
    }

    private Order mapRow(ResultSet rs) throws SQLException {
        Order o = new Order();
        o.setId(rs.getInt("id"));
        o.setCustomerId(rs.getInt("customer_id"));
        o.setRestaurantId(rs.getInt("restaurant_id"));
        int dpId = rs.getInt("delivery_person_id");
        o.setDeliveryPersonId(rs.wasNull() ? null : dpId);
        o.setStatus(rs.getString("status"));
        o.setTotalAmount(rs.getBigDecimal("total_amount"));
        o.setDeliveryAddress(rs.getString("delivery_address"));
        int eta = rs.getInt("eta_minutes");
        o.setEtaMinutes(rs.wasNull() ? null : eta);
        o.setCreatedAt(rs.getTimestamp("created_at"));

        try { o.setCustomerName(rs.getString("customer_name")); } catch (SQLException ignored) {}
        try { o.setRestaurantName(rs.getString("restaurant_name")); } catch (SQLException ignored) {}
        try { o.setDeliveryPersonName(rs.getString("delivery_name")); } catch (SQLException ignored) {}
        return o;
    }
}
